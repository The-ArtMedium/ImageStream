package org.satdiva.localclip

import android.content.ContentValues
import android.content.Context
import android.graphics.Bitmap
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.MediaMetadataRetriever
import android.media.MediaMuxer
import android.net.Uri
import android.provider.MediaStore
import java.nio.ByteBuffer

object Media {

    /** Start time (ms) of the keyframe at or before atMs, or -1 if unknown. */
    fun keyframeBefore(ctx: Context, src: Uri, atMs: Long): Long {
        val ex = MediaExtractor()
        try {
            ctx.contentResolver.openFileDescriptor(src, "r")!!.use { ex.setDataSource(it.fileDescriptor) }
            var vt = -1
            for (i in 0 until ex.trackCount) {
                val mime = ex.getTrackFormat(i).getString(MediaFormat.KEY_MIME) ?: continue
                if (mime.startsWith("video/")) { vt = i; break }
            }
            if (vt < 0) return -1L
            ex.selectTrack(vt)
            ex.seekTo(atMs * 1000, MediaExtractor.SEEK_TO_PREVIOUS_SYNC)
            return ex.sampleTime / 1000
        } catch (e: Exception) {
            return -1L
        } finally {
            ex.release()
        }
    }

    /** Evenly spaced thumbnails for the film strip. */
    fun thumbnails(ctx: Context, src: Uri, durMs: Long, n: Int): List<Bitmap> {
        val list = ArrayList<Bitmap>()
        val r = MediaMetadataRetriever()
        try {
            r.setDataSource(ctx, src)
            for (i in 0 until n) {
                val t = (durMs * 1000L * (2 * i + 1)) / (2 * n)
                val f = r.getFrameAtTime(t, MediaMetadataRetriever.OPTION_CLOSEST_SYNC)
                if (f != null) {
                    val sw = 240
                    val sh = maxOf(1, f.height * sw / f.width)
                    list.add(Bitmap.createScaledBitmap(f, sw, sh, true))
                }
            }
        } catch (e: Exception) {
            // thumbnails are optional
        } finally {
            r.release()
        }
        return list
    }

    /** Lossless stream copy. Returns the output file name. */
    fun trim(ctx: Context, src: Uri, startUs: Long, endUs: Long): String {
        val name = "clip_${System.currentTimeMillis()}.mp4"
        val values = ContentValues().apply {
            put(MediaStore.Video.Media.DISPLAY_NAME, name)
            put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
            put(MediaStore.Video.Media.RELATIVE_PATH, "Movies/LocalClip")
            put(MediaStore.Video.Media.IS_PENDING, 1)
        }
        val outUri = ctx.contentResolver.insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values)
            ?: throw IllegalStateException("cannot create output file")

        val extractor = MediaExtractor()
        var muxer: MediaMuxer? = null
        var ok = false
        try {
            ctx.contentResolver.openFileDescriptor(src, "r")!!.use { extractor.setDataSource(it.fileDescriptor) }
            ctx.contentResolver.openFileDescriptor(outUri, "rw")!!.use { pfd ->
                muxer = MediaMuxer(pfd.fileDescriptor, MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4)
                val m = muxer!!

                val mmr = MediaMetadataRetriever()
                try {
                    mmr.setDataSource(ctx, src)
                    mmr.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_ROTATION)
                        ?.toIntOrNull()?.let { m.setOrientationHint(it) }
                } finally { mmr.release() }

                val map = HashMap<Int, Int>()
                var maxSize = 64 * 1024
                for (i in 0 until extractor.trackCount) {
                    val f = extractor.getTrackFormat(i)
                    val mime = f.getString(MediaFormat.KEY_MIME) ?: continue
                    if (mime.startsWith("video/") || mime.startsWith("audio/")) {
                        extractor.selectTrack(i)
                        map[i] = m.addTrack(f)
                        if (f.containsKey(MediaFormat.KEY_MAX_INPUT_SIZE))
                            maxSize = maxOf(maxSize, f.getInteger(MediaFormat.KEY_MAX_INPUT_SIZE))
                    }
                }
                if (map.isEmpty()) throw IllegalStateException("no audio/video tracks")

                extractor.seekTo(startUs, MediaExtractor.SEEK_TO_PREVIOUS_SYNC)
                m.start()
                val buf = ByteBuffer.allocate(maxSize)
                val info = android.media.MediaCodec.BufferInfo()
                var base = -1L
                while (true) {
                    val size = extractor.readSampleData(buf, 0)
                    if (size < 0) break
                    val t = extractor.sampleTime
                    if (t > endUs) break
                    if (base < 0) base = t
                    info.offset = 0
                    info.size = size
                    info.presentationTimeUs = maxOf(0L, t - base)
                    info.flags = if (extractor.sampleFlags and MediaExtractor.SAMPLE_FLAG_SYNC != 0)
                        android.media.MediaCodec.BUFFER_FLAG_KEY_FRAME else 0
                    m.writeSampleData(map[extractor.sampleTrackIndex]!!, buf, info)
                    extractor.advance()
                }
                m.stop()
            }
            ok = true
        } finally {
            try { muxer?.release() } catch (_: Exception) {}
            extractor.release()
            if (ok) {
                ctx.contentResolver.update(outUri, ContentValues().apply {
                    put(MediaStore.Video.Media.IS_PENDING, 0)
                }, null, null)
            } else {
                ctx.contentResolver.delete(outUri, null, null)
            }
        }
        return name
    }
}
