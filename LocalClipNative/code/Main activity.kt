package org.satdiva.localclip

import android.app.Activity
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Intent
import android.graphics.Color
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.MediaMetadataRetriever
import android.media.MediaMuxer
import android.net.Uri
import android.os.Bundle
import android.provider.MediaStore
import android.view.Gravity
import android.view.ViewGroup
import android.widget.*
import java.nio.ByteBuffer
import java.util.Locale

class MainActivity : Activity() {

    private lateinit var video: VideoView
    private lateinit var seek: SeekBar
    private lateinit var info: TextView
    private lateinit var status: TextView
    private var uri: Uri? = null
    private var durationMs = 0L
    private var inMs = 0L
    private var outMs = 0L

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        buildUi()
        kofiEveryFifthLaunch()
    }

    private fun btn(label: String, onClick: () -> Unit) = Button(this).apply {
        text = label
        setOnClickListener { onClick() }
        layoutParams = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
    }

    private fun buildUi() {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(Color.parseColor("#0f0f0f"))
            setPadding(24, 48, 24, 24)
        }
        val title = TextView(this).apply {
            text = "LocalClip"; textSize = 26f; setTextColor(Color.parseColor("#f5a623"))
            gravity = Gravity.CENTER
        }
        video = VideoView(this)
        seek = SeekBar(this)
        info = TextView(this).apply { setTextColor(Color.WHITE); text = "Pick a video to begin." }
        status = TextView(this).apply { setTextColor(Color.parseColor("#52b788")) }

        val row1 = LinearLayout(this).apply {
            addView(btn("Open video") { pick() })
            addView(btn("Set IN") { inMs = video.currentPosition.toLong(); refresh() })
            addView(btn("Set OUT") { outMs = video.currentPosition.toLong(); refresh() })
        }
        val row2 = LinearLayout(this).apply {
            addView(btn("Play / Pause") { if (video.isPlaying) video.pause() else video.start() })
            addView(btn("Save lossless clip") { save() })
        }

        root.addView(title)
        root.addView(video, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        root.addView(seek)
        root.addView(info)
        root.addView(row1)
        root.addView(row2)
        root.addView(status)
        setContentView(root)

        seek.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(s: SeekBar?, p: Int, fromUser: Boolean) {
                if (fromUser) { video.seekTo(p); refresh() }
            }
            override fun onStartTrackingTouch(s: SeekBar?) { video.pause() }
            override fun onStopTrackingTouch(s: SeekBar?) {}
        })
    }

    private fun fmt(ms: Long): String {
        val s = ms / 1000.0
        return String.format(Locale.US, "%d:%05.2f", (s / 60).toInt(), s % 60)
    }

    private fun refresh() {
        info.text = "IN ${fmt(inMs)}   OUT ${fmt(outMs)}   of ${fmt(durationMs)}\n" +
            "Cuts snap to the nearest earlier keyframe (no re-encoding, no quality loss)."
    }

    private fun pick() {
        val i = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE); type = "video/*"
        }
        startActivityForResult(i, 1)
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != 1 || resultCode != RESULT_OK) return
        val u = data?.data ?: return
        uri = u
        val mmr = MediaMetadataRetriever()
        try {
            mmr.setDataSource(this, u)
            durationMs = mmr.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLong() ?: 0L
        } catch (e: Exception) {
            status.text = "Could not read that file: ${e.message}"; return
        } finally { mmr.release() }
        inMs = 0; outMs = durationMs
        seek.max = durationMs.toInt()
        video.setVideoURI(u)
        video.setOnPreparedListener { video.seekTo(1) }
        status.text = ""
        refresh()
    }

    private fun save() {
        val src = uri ?: run { status.text = "Open a video first."; return }
        if (outMs <= inMs) { status.text = "OUT must be after IN."; return }
        status.text = "Saving…"
        val a = inMs; val b = outMs
        Thread {
            val msg = try {
                val name = trim(src, a * 1000, b * 1000)
                "Saved to Movies/LocalClip/$name"
            } catch (e: Exception) {
                "Could not save: ${e.message}"
            }
            runOnUiThread { status.text = msg }
        }.start()
    }

    /** Lossless stream copy. Returns the output file name. */
    private fun trim(src: Uri, startUs: Long, endUs: Long): String {
        val name = "clip_${System.currentTimeMillis()}.mp4"
        val values = ContentValues().apply {
            put(MediaStore.Video.Media.DISPLAY_NAME, name)
            put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
            put(MediaStore.Video.Media.RELATIVE_PATH, "Movies/LocalClip")
            put(MediaStore.Video.Media.IS_PENDING, 1)
        }
        val outUri = contentResolver.insert(MediaStore.Video.Media.EXTERNAL_CONTENT_URI, values)
            ?: throw IllegalStateException("cannot create output file")

        val extractor = MediaExtractor()
        var muxer: MediaMuxer? = null
        var ok = false
        try {
            contentResolver.openFileDescriptor(src, "r")!!.use { extractor.setDataSource(it.fileDescriptor) }
            contentResolver.openFileDescriptor(outUri, "rw")!!.use { pfd ->
                muxer = MediaMuxer(pfd.fileDescriptor, MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4)
                val m = muxer!!

                val mmr = MediaMetadataRetriever()
                try {
                    mmr.setDataSource(this, src)
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
                val bi = MediaCodec.BufferInfo()
                var base = -1L
                while (true) {
                    val size = extractor.readSampleData(buf, 0)
                    if (size < 0) break
                    val t = extractor.sampleTime
                    if (t > endUs) break
                    if (base < 0) base = t
                    bi.offset = 0
                    bi.size = size
                    bi.presentationTimeUs = maxOf(0L, t - base)
                    bi.flags = if (extractor.sampleFlags and MediaExtractor.SAMPLE_FLAG_SYNC != 0)
                        MediaCodec.BUFFER_FLAG_KEY_FRAME else 0
                    m.writeSampleData(map[extractor.sampleTrackIndex]!!, buf, bi)
                    extractor.advance()
                }
                m.stop()
            }
            ok = true
        } finally {
            try { muxer?.release() } catch (_: Exception) {}
            extractor.release()
            if (ok) {
                contentResolver.update(outUri, ContentValues().apply {
                    put(MediaStore.Video.Media.IS_PENDING, 0)
                }, null, null)
            } else {
                contentResolver.delete(outUri, null, null)
            }
        }
        return name
    }

    private fun kofiEveryFifthLaunch() {
        val p = getSharedPreferences("lc", MODE_PRIVATE)
        val n = p.getInt("launches", 0) + 1
        p.edit().putInt("launches", n).apply()
        if (n % 5 != 0) return
        AlertDialog.Builder(this)
            .setTitle("LocalClip is free")
            .setMessage("If it saved you time, a coffee keeps it going. No pressure.")
            .setPositiveButton("Ko-fi") { _, _ ->
                startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("https://ko-fi.com/1satdiva")))
            }
            .setNegativeButton("Not now", null)
            .show()
    }
}
