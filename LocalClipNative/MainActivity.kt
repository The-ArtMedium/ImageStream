package org.satdiva.localclip

import android.content.Intent
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Outline
import android.media.MediaMetadataRetriever
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.ViewOutlineProvider
import android.widget.Button
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import android.widget.VideoView
import android.graphics.drawable.ColorDrawable

class MainActivity : BaseActivity() {

    private lateinit var video: VideoView
    private lateinit var timeline: TimelineView
    private lateinit var posText: TextView
    private lateinit var durText: TextView
    private lateinit var rangeText: TextView
    private lateinit var snapText: TextView
    private lateinit var status: TextView
    private lateinit var thanksBtn: Button
    private lateinit var emptyView: View
    private var mp: MediaPlayer? = null
    private var uri: Uri? = null
    private var durationMs = 0L
    private var inMs = 0L
    private var outMs = 0L
    private var mainShown = false
    private var cachedFrames: List<Bitmap> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.setBackgroundDrawable(ColorDrawable(BG))
        window.statusBarColor = BG
        window.navigationBarColor = BG
        showSplash { goMain() }
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        if (mainShown) {
            val keep = uri
            val pos = if (keep != null) video.currentPosition else 0
            buildUi()
            if (keep != null) loadVideo(keep, pos, false)
        }
    }

    override fun onDestroy() {
        ui.removeCallbacksAndMessages(null)
        super.onDestroy()
    }

    private fun goMain() {
        if (mainShown) return
        mainShown = true
        buildUi()
        kofiSometimes()
    }

    // ---------- main screen ----------

    private fun buildUi() {
        val landscape = resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE

        val root = LinearLayout(this)
        root.orientation = LinearLayout.VERTICAL
        root.setBackgroundColor(BG)
        root.fitsSystemWindows = true

        // header: logo + name + Ko-fi + close
        val header = LinearLayout(this)
        header.orientation = LinearLayout.HORIZONTAL
        header.gravity = Gravity.CENTER_VERTICAL
        header.setPadding(dp(16), dp(8), dp(12), dp(8))
        val logo = ImageView(this)
        logo.setImageResource(R.mipmap.ic_launcher)
        logo.clipToOutline = true
        logo.outlineProvider = object : ViewOutlineProvider() {
            override fun getOutline(v: View, outline: Outline) {
                outline.setRoundRect(0, 0, v.width, v.height, dp(10).toFloat())
            }
        }
        header.addView(logo, LinearLayout.LayoutParams(dp(44), dp(44)))
        val titles = LinearLayout(this)
        titles.orientation = LinearLayout.VERTICAL
        titles.setPadding(dp(12), 0, 0, 0)
        titles.addView(label("LocalClip", 22f, GOLD, true))
        titles.addView(label("Lossless · Local · No recompression", 11f, DIM))
        header.addView(titles, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        header.addView(kofiButton())
        val closeBtn = pill("✕", KEY, Color.WHITE) { finish() }
        closeBtn.minWidth = dp(44)
        closeBtn.minimumWidth = dp(44)
        closeBtn.minHeight = dp(40)
        closeBtn.minimumHeight = dp(40)
        val closeLp = LinearLayout.LayoutParams(dp(48), ViewGroup.LayoutParams.WRAP_CONTENT)
        closeLp.leftMargin = dp(8)
        header.addView(closeBtn, closeLp)
        root.addView(header)

        // stage: video + empty state
        val stage = FrameLayout(this)
        stage.setBackgroundColor(Color.BLACK)
        video = VideoView(this)
        stage.addView(video, FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT, Gravity.CENTER))
        val empty = LinearLayout(this)
        empty.orientation = LinearLayout.VERTICAL
        empty.gravity = Gravity.CENTER
        empty.setBackgroundColor(Color.BLACK)
        val msg = label("Choose a video to trim", 16f, DIM)
        msg.gravity = Gravity.CENTER
        empty.addView(msg)
        val big = pill("Open video", GOLD, Color.BLACK) { pick() }
        val bigLp = LinearLayout.LayoutParams(dp(220), ViewGroup.LayoutParams.WRAP_CONTENT)
        bigLp.topMargin = dp(16)
        empty.addView(big, bigLp)
        emptyView = empty
        stage.addView(empty, FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))

        // timeline (film strip)
        timeline = TimelineView(this)
        timeline.frames = cachedFrames
        timeline.onScrub = { ms ->
            seekExact(ms.toInt())
            posText.text = fmt(ms)
        }
        timeline.onInChanged = { ms -> inMs = ms; refresh() }
        timeline.onOutChanged = { ms -> outMs = ms; refresh() }
        timeline.onEdit = { checkSnap() }
        val timelineWrap = FrameLayout(this)
        timelineWrap.setBackgroundColor(PANEL)
        timelineWrap.setPadding(dp(10), dp(8), dp(10), dp(2))
        timelineWrap.addView(timeline, FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))

        // controls panel
        val panel = LinearLayout(this)
        panel.orientation = LinearLayout.VERTICAL
        panel.setPadding(dp(10), dp(8), dp(10), dp(8))

        posText = label("00:00.000", 30f, Color.WHITE, true)
        posText.gravity = Gravity.CENTER
        panel.addView(posText)
        durText = label("", 12f, DIM)
        durText.gravity = Gravity.CENTER
        panel.addView(durText)

        panel.addView(row(
            pill("−60s", KEY, Color.WHITE, true) { nudge(-60000) },
            pill("−30s", KEY, Color.WHITE, true) { nudge(-30000) },
            pill("−10s", KEY, Color.WHITE, true) { nudge(-10000) },
            pill("+10s", KEY, Color.WHITE, true) { nudge(10000) },
            pill("+30s", KEY, Color.WHITE, true) { nudge(30000) },
            pill("+60s", KEY, Color.WHITE, true) { nudge(60000) }
        ))
        panel.addView(row(
            pill("−3s", Color.parseColor("#3A4757"), Color.WHITE, true) { nudge(-3000) },
            pill("−1s", Color.parseColor("#3A4757"), Color.WHITE, true) { nudge(-1000) },
            pill("+1s", Color.parseColor("#3A4757"), Color.WHITE, true) { nudge(1000) },
            pill("+3s", Color.parseColor("#3A4757"), Color.WHITE, true) { nudge(3000) }
        ))
        panel.addView(row(
            pill("−200ms", KEY, Color.WHITE, true) { nudge(-200) },
            pill("−50ms", KEY, Color.WHITE, true) { nudge(-50) },
            pill("+50ms", KEY, Color.WHITE, true) { nudge(50) },
            pill("+200ms", KEY, Color.WHITE, true) { nudge(200) }
        ))
        panel.addView(row(
            pill("Play / Pause", KEY, Color.WHITE) {
                if (uri != null) { if (video.isPlaying) video.pause() else video.start() }
            }
        ))
        panel.addView(row(
            pill("Set IN", TEAL, Color.BLACK) {
                if (uri != null) { inMs = video.currentPosition.toLong(); refresh(); checkSnap() }
            },
            pill("Set OUT", GOLD, Color.BLACK) {
                if (uri != null) { outMs = video.currentPosition.toLong(); refresh() }
            }
        ))

        rangeText = label("", 13f, Color.WHITE, true)
        rangeText.gravity = Gravity.CENTER
        panel.addView(rangeText)
        snapText = label("", 12f, TEAL)
        snapText.gravity = Gravity.CENTER
        panel.addView(snapText)

        panel.addView(row(
            pill("Open video", KEY, Color.WHITE) { pick() },
            pill("Save lossless clip", GOLD, Color.BLACK) { save() }
        ))
        status = label("", 13f, Color.parseColor("#52B788"))
        status.gravity = Gravity.CENTER
        panel.addView(status)

        thanksBtn = pill("☕ Thank you! Say thanks on Ko-fi", GOLD, Color.BLACK) { openKofi() }
        thanksBtn.visibility = View.GONE
        val thanksLp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        thanksLp.setMargins(dp(3), dp(6), dp(3), dp(3))
        panel.addView(thanksBtn, thanksLp)

        val hint = label(
            "Drag the gold edges on the film strip to choose what to keep. Tap the strip to move the playhead. " +
                "Original quality, no re-encoding: the start snaps back to the nearest earlier keyframe; the end lands on the frame.",
            11f, DIM)
        hint.gravity = Gravity.CENTER
        panel.addView(hint)

        val love = label(
            "Made with love by Satdiva. LocalClip is free, private and works offline: no ads, no tracking. " +
                "If it helps your work, a coffee on Ko-fi keeps it going. Thank you!",
            12f, GOLD)
        love.gravity = Gravity.CENTER
        love.setPadding(dp(8), dp(10), dp(8), dp(4))
        love.setOnClickListener { openKofi() }
        panel.addView(love)

        val scroll = ScrollView(this)
        scroll.setBackgroundColor(PANEL)
        scroll.addView(panel, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))

        if (landscape) {
            val body = LinearLayout(this)
            body.orientation = LinearLayout.HORIZONTAL
            body.addView(stage, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 3f))
            body.addView(scroll, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 2f))
            root.addView(body, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
            root.addView(timelineWrap, LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
        } else {
            root.addView(stage, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
            root.addView(timelineWrap, LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))
            root.addView(scroll, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1.3f))
        }
        setContentView(root)

        refresh()
        ui.removeCallbacks(tick)
        ui.post(tick)
    }

    private val tick: Runnable = object : Runnable {
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
    private fun seekExact(ms: Int) {
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

    private fun nudge(deltaMs: Int) {
        if (uri == null) return
        val target = (video.currentPosition + deltaMs).coerceIn(0, durationMs.toInt())
        video.pause()
        seekExact(target)
        posText.text = fmt(target.toLong())
        timeline.posMs = target.toLong()
        timeline.invalidate()
    }

    private fun refresh() {
        durText.text = if (durationMs > 0) "of " + fmt(durationMs) else ""
        val len = if (outMs > inMs) fmt(outMs - inMs) else fmt(0)
        rangeText.text = "IN " + fmt(inMs) + "    OUT " + fmt(outMs) + "    LENGTH " + len
        timeline.durationMs = durationMs
        timeline.inMs = inMs
        timeline.outMs = outMs
        timeline.invalidate()
    }

    /** Shows where the lossless cut will really start (nearest earlier keyframe). */
    private fun checkSnap() {
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

    private fun loadFrames(u: Uri) {
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

    private fun pick() {
        val i = Intent(Intent.ACTION_OPEN_DOCUMENT)
        i.addCategory(Intent.CATEGORY_OPENABLE)
        i.type = "video/*"
        startActivityForResult(i, 1)
    }

    private fun loadVideo(u: Uri, startAt: Int, newFile: Boolean) {
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

    private fun save() {
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
