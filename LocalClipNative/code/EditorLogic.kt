package org.satdiva.localclip

import android.content.Intent
import android.graphics.Bitmap
import android.media.MediaMetadataRetriever
import android.media.MediaPlayer
import android.net.Uri
import android.view.View
import android.widget.Button
import android.widget.TextView
import android.widget.VideoView

/** Editor state + behaviour (no layout). MainActivity builds the screen. */
abstract class EditorLogic : BaseActivity() {

    lateinit var video: VideoView
    lateinit var timeline: TimelineView
    lateinit var posText: TextView
    lateinit var durText: TextView
    lateinit var rangeText: TextView
    lateinit var snapText: TextView
    lateinit var status: TextView
    lateinit var thanksBtn: Button
    lateinit var emptyView: View
    var mp: MediaPlayer? = null
    var uri: Uri? = null
    var durationMs = 0L
    var inMs = 0L
    var outMs = 0L
    var mainShown = false
    var cachedFrames: List<Bitmap> = emptyList()

    val tick: Runnable = object : Runnable {
        override fun run() {
            if (uri != null && mainShown && !timeline.touching) {
                val p = video.currentPosition
                timeline.posMs = p.toLong()
                timeline.invalidate()
                posText.text = fmt(p.toLong())
            }
            ui.postDelayed(this, 150)
        }
    }

    /** Frame-accurate seek (the plain VideoView.seekTo jumps to keyframes). */
    fun seekExact(ms: Int) {
        val m = mp
        if (m != null) {
            try {
                m.seekTo(ms.toLong(), MediaPlayer.SEEK_CLOSEST)
            } catch (e: Exception) {
                video.seekTo(ms)
            }
        } else {
            video.seekTo(ms)
        }
    }

    fun nudge(deltaMs: Int) {
        if (uri == null) return
        val target = (video.currentPosition + deltaMs).coerceIn(0, durationMs.toInt())
        video.pause()
        seekExact(target)
        posText.text = fmt(target.toLong())
        timeline.posMs = target.toLong()
        timeline.invalidate()
    }

    fun refresh() {
        durText.text = if (durationMs > 0) "of " + fmt(durationMs) else ""
        val len = if (outMs > inMs) fmt(outMs - inMs) else fmt(0)
        rangeText.text = "IN " + fmt(inMs) + "    OUT " + fmt(outMs) + "    LENGTH " + len
        timeline.durationMs = durationMs
        timeline.inMs = inMs
        timeline.outMs = outMs
        timeline.invalidate()
    }

    /** Shows where the lossless cut will really start (nearest earlier keyframe). */
    fun checkSnap() {
        val src = uri ?: return
        val at = inMs
        Thread {
            val snapMs = Media.keyframeBefore(this, src, at)
            val txt = if (snapMs < 0) ""
            else if (snapMs >= at - 20) "Start is on a keyframe: exact."
            else "Start will snap back to " + fmt(snapMs) + " (nearest earlier keyframe)."
            runOnUiThread { snapText.text = txt }
        }.start()
    }

    fun loadFrames(u: Uri) {
        val dur = durationMs
        Thread {
            val list = Media.thumbnails(this, u, dur, 12)
            runOnUiThread {
                cachedFrames = list
                timeline.frames = list
                timeline.invalidate()
            }
        }.start()
    }

    // ---------- picking ----------

    fun pick() {
        val i = Intent(Intent.ACTION_OPEN_DOCUMENT)
        i.addCategory(Intent.CATEGORY_OPENABLE)
        i.type = "video/*"
        startActivityForResult(i, 1)
    }

    fun loadVideo(u: Uri, startAt: Int, newFile: Boolean) {
        emptyView.visibility = View.GONE
        video.setVideoURI(u)
        video.setOnPreparedListener { m ->
            mp = m
            seekExact(if (startAt > 0) startAt else 1)
        }
        timeline.posMs = startAt.toLong()
        refresh()
        if (newFile) loadFrames(u)
    }

    @Deprecated("Deprecated in Java")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode != 1 || resultCode != RESULT_OK) return
        val u = data?.data ?: return
        val mmr = MediaMetadataRetriever()
        try {
            mmr.setDataSource(this, u)
            durationMs = mmr.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION)?.toLong() ?: 0L
        } catch (e: Exception) {
            status.text = "Could not read that file: " + e.message
            return
        } finally { mmr.release() }
        uri = u
        inMs = 0
        outMs = durationMs
        cachedFrames = emptyList()
        timeline.frames = cachedFrames
        status.text = ""
        snapText.text = ""
        thanksBtn.visibility = View.GONE
        loadVideo(u, 0, true)
    }

    fun save() {
        val src = uri
        if (src == null) { status.text = "Open a video first."; return }
        if (outMs <= inMs) { status.text = "OUT must be after IN."; return }
        status.text = "Saving…"
        thanksBtn.visibility = View.GONE
        val a = inMs
        val b = outMs
        Thread {
            var ok = false
            val msg = try {
                val name = Media.trim(this, src, a * 1000, b * 1000)
                ok = true
                "Saved to Movies/LocalClip/" + name
            } catch (e: Exception) {
                "Could not save: " + e.message
            }
            runOnUiThread {
                status.text = msg
                if (ok) thanksBtn.visibility = View.VISIBLE
            }
        }.start()
    }
}
