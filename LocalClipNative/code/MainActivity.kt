package org.satdiva.localclip

import android.app.Activity
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Intent
import android.content.res.ColorStateList
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.MediaMetadataRetriever
import android.media.MediaMuxer
import android.media.MediaPlayer
import android.net.Uri
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.MediaStore
import android.util.Base64
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.SeekBar
import android.widget.TextView
import android.widget.VideoView
import java.nio.ByteBuffer
import java.util.Locale

class MainActivity : Activity() {

    private val BG = Color.parseColor("#0B0F14")
    private val PANEL = Color.parseColor("#18202A")
    private val GOLD = Color.parseColor("#F5A623")
    private val TEAL = Color.parseColor("#2EC4B6")
    private val DIM = Color.parseColor("#9AA7B4")
    private val KEY = Color.parseColor("#2A3441")
    private val KOFI_URL = "https://ko-fi.com/1satdiva"

    private val ui = Handler(Looper.getMainLooper())
    private lateinit var video: VideoView
    private lateinit var seek: SeekBar
    private lateinit var posText: TextView
    private lateinit var durText: TextView
    private lateinit var rangeText: TextView
    private lateinit var snapText: TextView
    private lateinit var hint: TextView
    private lateinit var status: TextView
    private lateinit var emptyView: View
    private var mp: MediaPlayer? = null
    private var uri: Uri? = null
    private var durationMs = 0L
    private var inMs = 0L
    private var outMs = 0L
    private var mainShown = false
    private var dragging = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = BG
        window.navigationBarColor = BG
        showSplash()
    }

    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        if (mainShown) {
            val keep = uri
            val pos = if (keep != null) video.currentPosition else 0
            buildUi()
            if (keep != null) loadVideo(keep, pos)
        }
    }

    override fun onDestroy() {
        ui.removeCallbacksAndMessages(null)
        super.onDestroy()
    }

    // ---------- helpers ----------

    private fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()

    private fun bmp(b64: String): Bitmap? {
        return try {
            val bytes = Base64.decode(b64, Base64.DEFAULT)
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        } catch (e: Exception) { null }
    }

    private fun pill(label: String, bg: Int, fg: Int, small: Boolean = false, onClick: () -> Unit): Button {
        val b = Button(this)
        b.text = label
        b.isAllCaps = false
        b.textSize = if (small) 13f else 15f
        b.setTextColor(fg)
        val h = if (small) dp(40) else dp(48)
        b.minHeight = h
        b.minimumHeight = h
        b.setPadding(dp(4), 0, dp(4), 0)
        b.stateListAnimator = null
        val shape = GradientDrawable()
        shape.cornerRadius = dp(24).toFloat()
        shape.setColor(bg)
        b.background = shape
        b.setOnClickListener { onClick() }
        return b
    }

    private fun row(vararg views: View): LinearLayout {
        val r = LinearLayout(this)
        r.orientation = LinearLayout.HORIZONTAL
        for (v in views) {
            val lp = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            lp.setMargins(dp(3), dp(3), dp(3), dp(3))
            r.addView(v, lp)
        }
        return r
    }

    private fun label(text: String, size: Float, color: Int, bold: Boolean = false): TextView {
        val t = TextView(this)
        t.text = text
        t.textSize = size
        t.setTextColor(color)
        if (bold) t.setTypeface(t.typeface, android.graphics.Typeface.BOLD)
        return t
    }

    private fun openKofi() {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(KOFI_URL)))
        } catch (e: Exception) { /* no browser available */ }
    }

    private fun kofiButton(): Button {
        val b = pill("☕ Ko-fi", GOLD, Color.BLACK) { openKofi() }
        b.minHeight = dp(40)
        b.minimumHeight = dp(40)
        b.textSize = 14f
        return b
    }

    /** mm:ss.mmm */
    private fun fmt(ms: Long): String {
        val m = if (ms < 0) 0L else ms
        val total = m / 1000
        return String.format(Locale.US, "%02d:%02d.%03d", total / 60, total % 60, m % 1000)
    }

    // ---------- splash ----------

    private fun showSplash() {
        val f = FrameLayout(this)
        f.setBackgroundColor(BG)
        val img = ImageView(this)
        img.scaleType = ImageView.ScaleType.CENTER_INSIDE
        img.setImageBitmap(bmp(Images.splash))
        f.addView(img, FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        val lp = FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT,
            Gravity.BOTTOM or Gravity.END)
        lp.setMargins(0, 0, dp(16), dp(16))
        f.addView(kofiButton(), lp)
        f.setOnClickListener { goMain() }
        setContentView(f)
        ui.postDelayed({ goMain() }, 2500)
    }

    private fun goMain() {
        if (mainShown) return
        mainShown = true
        buildUi()
        kofiEveryFifthLaunch()
    }

    // ---------- main screen ----------

    private fun buildUi() {
        val landscape = resources.configuration.orientation == Configuration.ORIENTATION_LANDSCAPE

        val root = LinearLayout(this)
        root.orientation = LinearLayout.VERTICAL
        root.setBackgroundColor(BG)
        root.fitsSystemWindows = true

        // header: logo + name + Ko-fi
        val header = LinearLayout(this)
        header.orientation = LinearLayout.HORIZONTAL
        header.gravity = Gravity.CENTER_VERTICAL
        header.setPadding(dp(16), dp(8), dp(16), dp(8))
        val logo = ImageView(this)
        logo.setImageBitmap(bmp(Images.logo))
        header.addView(logo, LinearLayout.LayoutParams(dp(44), dp(44)))
        val titles = LinearLayout(this)
        titles.orientation = LinearLayout.VERTICAL
        titles.setPadding(dp(12), 0, 0, 0)
        titles.addView(label("LocalClip", 22f, GOLD, true))
        titles.addView(label("Lossless · Local · No recompression", 11f, DIM))
        header.addView(titles, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        header.addView(kofiButton())
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

        seek = SeekBar(this)
        seek.progressTintList = ColorStateList.valueOf(GOLD)
        seek.thumbTintList = ColorStateList.valueOf(GOLD)
        panel.addView(seek)

        // coarse, medium and fine steps (same ladder as the first LocalClip)
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
        hint = label("Original quality, no re-encoding. The start snaps back to the nearest earlier keyframe; the end lands on the frame.", 11f, DIM)
        hint.gravity = Gravity.CENTER
        panel.addView(hint)
        status = label("", 13f, Color.parseColor("#52B788"))
        status.gravity = Gravity.CENTER
        panel.addView(status)

        val scroll = ScrollView(this)
        scroll.setBackgroundColor(PANEL)
        scroll.addView(panel, ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))

        val body = LinearLayout(this)
        if (landscape) {
            body.orientation = LinearLayout.HORIZONTAL
            body.addView(stage, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 3f))
            body.addView(scroll, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.MATCH_PARENT, 2f))
        } else {
            body.orientation = LinearLayout.VERTICAL
            body.addView(stage, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
            body.addView(scroll, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1.3f))
        }
        root.addView(body, LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))
        setContentView(root)

        seek.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(s: SeekBar?, p: Int, fromUser: Boolean) {
                if (fromUser && uri != null) {
                    seekExact(p)
                    posText.text = fmt(p.toLong())
                }
            }
            override fun onStartTrackingTouch(s: SeekBar?) { dragging = true; if (uri != null) video.pause() }
            override fun onStopTrackingTouch(s: SeekBar?) { dragging = false }
        })

        refresh()
        ui.removeCallbacks(tick)
        ui.post(tick)
    }

    private val tick: Runnable = object : Runnable {
        override fun run() {
            if (uri != null && !dragging && mainShown) {
                val p = video.currentPosition
                seek.progress = p
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
        seek.progress = target
    }

    private fun refresh() {
        durText.text = if (durationMs > 0) "of " + fmt(durationMs) else ""
        val len = if (outMs > inMs) fmt(outMs - inMs) else fmt(0)
        rangeText.text = "IN " + fmt(inMs) + "    OUT " + fmt(outMs) + "    LENGTH " + len
    }

    /** Shows where the lossless cut will really start (nearest earlier keyframe). */
    private fun checkSnap() {
        val src = uri ?: return
        val at = inMs
        Thread {
            var txt = ""
            val ex = MediaExtractor()
            try {
                contentResolver.openFileDescriptor(src, "r")!!.use { ex.setDataSource(it.fileDescriptor) }
                var vt = -1
                for (i in 0 until ex.trackCount) {
                    val mime = ex.getTrackFormat(i).getString(MediaFormat.KEY_MIME) ?: continue
                    if (mime.startsWith("video/")) { vt = i; break }
                }
                if (vt >= 0) {
                    ex.selectTrack(vt)
                    ex.seekTo(at * 1000, MediaExtractor.SEEK_TO_PREVIOUS_SYNC)
                    val snapMs = ex.sampleTime / 1000
                    txt = if (snapMs >= at - 20) "Start is on a keyframe: exact."
                    else "Start will snap back to " + fmt(snapMs) + " (nearest earlier keyframe)."
                }
            } catch (e: Exception) {
                txt = ""
            } finally {
                ex.release()
            }
            runOnUiThread { snapText.text = txt }
        }.start()
    }

    // ---------- picking ----------

    private fun pick() {
        val i = Intent(Intent.ACTION_OPEN_DOCUMENT)
        i.addCategory(Intent.CATEGORY_OPENABLE)
        i.type = "video/*"
        startActivityForResult(i, 1)
    }

    private fun loadVideo(u: Uri, startAt: Int) {
        seek.max = durationMs.toInt()
        seek.progress = startAt
        emptyView.visibility = View.GONE
        video.setVideoURI(u)
        video.setOnPreparedListener { m ->
            mp = m
            seekExact(if (startAt > 0) startAt else 1)
        }
        refresh()
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
        status.text = ""
        snapText.text = ""
        loadVideo(u, 0)
    }

    private fun save() {
        val src = uri
        if (src == null) { status.text = "Open a video first."; return }
        if (outMs <= inMs) { status.text = "OUT must be after IN."; return }
        status.text = "Saving…"
        val a = inMs
        val b = outMs
        Thread {
            val msg = try {
                val name = trim(src, a * 1000, b * 1000)
                "Saved to Movies/LocalClip/" + name
            } catch (e: Exception) {
                "Could not save: " + e.message
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
            .setPositiveButton("Ko-fi") { _, _ -> openKofi() }
            .setNegativeButton("Not now", null)
            .show()
    }
}
