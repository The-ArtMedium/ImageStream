package org.satdiva.localclip

import android.app.Activity
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.media.MediaCodec
import android.media.MediaExtractor
import android.media.MediaFormat
import android.media.MediaMetadataRetriever
import android.media.MediaMuxer
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
    private val KOFI_URL = "https://ko-fi.com/1satdiva"

    private val ui = Handler(Looper.getMainLooper())
    private lateinit var video: VideoView
    private lateinit var seek: SeekBar
    private lateinit var posText: TextView
    private lateinit var inText: TextView
    private lateinit var outText: TextView
    private lateinit var hint: TextView
    private lateinit var status: TextView
    private lateinit var emptyView: View
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

    private fun pill(label: String, bg: Int, fg: Int, onClick: () -> Unit): Button {
        val b = Button(this)
        b.text = label
        b.isAllCaps = false
        b.textSize = 15f
        b.setTextColor(fg)
        b.minHeight = dp(48)
        b.minimumHeight = dp(48)
        b.stateListAnimator = null
        val shape = GradientDrawable()
        shape.cornerRadius = dp(26).toFloat()
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
            lp.setMargins(dp(4), dp(4), dp(4), dp(4))
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
        val b = pill("\u2615 Ko-fi", GOLD, Color.BLACK) { openKofi() }
        b.minHeight = dp(40)
        b.minimumHeight = dp(40)
        b.textSize = 14f
        return b
    }

    private fun fmt(ms: Long): String {
        val s = ms / 1000.0
        return String.format(Locale.US, "%d:%05.2f", (s / 60).toInt(), s % 60)
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
        val root = LinearLayout(this)
        root.orientation = LinearLayout.VERTICAL
        root.setBackgroundColor(BG)
        root.fitsSystemWindows = true

        // header: logo + name + Ko-fi
        val header = LinearLayout(this)
        header.orientation = LinearLayout.HORIZONTAL
        header.gravity = Gravity.CENTER_VERTICAL
        header.setPadding(dp(16), dp(10), dp(16), dp(10))
        val logo = ImageView(this)
        logo.setImageBitmap(bmp(Images.logo))
        header.addView(logo, LinearLayout.LayoutParams(dp(46), dp(46)))
        val titles = LinearLayout(this)
        titles.orientation = LinearLayout.VERTICAL
        titles.setPadding(dp(12), 0, 0, 0)
        titles.addView(label("LocalClip", 22f, GOLD, true))
        titles.addView(label("Lossless \u00B7 Local \u00B7 No recompression", 11f, DIM))
        header.addView(titles, LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f))
        header.addView(kofiButton())
        root.addView(header)

        // stage: video + empty-state
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
        root.addView(stage, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f))

        // controls panel
        val panel = LinearLayout(this)
        panel.orientation = LinearLayout.VERTICAL
        panel.setBackgroundColor(PANEL)
        panel.setPadding(dp(12), dp(8), dp(12), dp(8))

        seek = SeekBar(this)
        seek.progressTintList = ColorStateList.valueOf(GOLD)
        seek.thumbTintList = ColorStateList.valueOf(GOLD)
        panel.addView(seek)

        inText = label("", 14f, TEAL, true)
        posText = label("0:00.00", 14f, Color.WHITE, true)
        posText.gravity = Gravity.CENTER
        outText = label("", 14f, GOLD, true)
        outText.gravity = Gravity.END
        panel.addView(row(inText, posText, outText))

        panel.addView(row(
            pill("\u2212 1 s", Color.parseColor("#2A3441"), Color.WHITE) { nudge(-1000) },
            pill("Play / Pause", Color.parseColor("#2A3441"), Color.WHITE) {
                if (uri != null) { if (video.isPlaying) video.pause() else video.start() }
            },
            pill("+ 1 s", Color.parseColor("#2A3441"), Color.WHITE) { nudge(1000) }
        ))
        panel.addView(row(
            pill("Set IN", TEAL, Color.BLACK) {
                if (uri != null) { inMs = video.currentPosition.toLong(); refresh() }
            },
            pill("Set OUT", GOLD, Color.BLACK) {
                if (uri != null) { outMs = video.currentPosition.toLong(); refresh() }
            }
        ))
        panel.addView(row(
            pill("Open video", Color.parseColor("#2A3441"), Color.WHITE) { pick() },
            pill("Save lossless clip", GOLD, Color.BLACK) { save() }
        ))

        hint = label("", 11f, DIM)
        hint.gravity = Gravity.CENTER
        panel.addView(hint)
        status = label("", 13f, Color.parseColor("#52B788"))
        status.gravity = Gravity.CENTER
        panel.addView(status)
        root.addView(panel, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT))

        setContentView(root)

        seek.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(s: SeekBar?, p: Int, fromUser: Boolean) {
                if (fromUser && uri != null) {
                    video.seekTo(p)
                    posText.text = fmt(p.toLong())
                }
            }
            override fun onStartTrackingTouch(s: SeekBar?) { dragging = true; if (uri != null) video.pause() }
            override fun onStopTrackingTouch(s: SeekBar?) { dragging = false }
        })

        refresh()
        ui.post(tick)
    }

    private val tick: Runnable = object : Runnable {
        override fun run() {
            if (uri != null && !dragging) {
                val p = video.currentPosition
                seek.progress = p
                posText.text = fmt(p.toLong())
            }
            ui.postDelayed(this, 150)
        }
    }

    private fun nudge(deltaMs: Int) {
        if (uri == null) return
        val target = (video.currentPosition + deltaMs).coerceIn(0, durationMs.toInt())
        video.pause()
        video.seekTo(target)
        posText.text = fmt(target.toLong())
        seek.progress = target
    }

    private fun refresh() {
        inText.text = "IN  " + fmt(inMs)
        outText.text = "OUT  " + fmt(outMs)
        val len = if (outMs > inMs) fmt(outMs - inMs) else "0:00.00"
        hint.text = "Clip length " + len +
            "  \u00B7  Cuts snap to the nearest earlier keyframe: no re-encoding, no quality loss."
    }

    // ---------- picking ----------

    private fun pick() {
        val i = Intent(Intent.ACTION_OPEN_DOCUMENT)
        i.addCategory(Intent.CATEGORY_OPENABLE)
        i.type = "video/*"
        startActivityForResult(i, 1)
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
        seek.max = durationMs.toInt()
        seek.progress = 0
        emptyView.visibility = View.GONE
        video.setVideoURI(u)
        video.setOnPreparedListener { video.seekTo(1) }
        status.text = ""
        refresh()
    }

    private fun save() {
        val src = uri
        if (src == null) { status.text = "Open a video first."; return }
        if (outMs <= inMs) { status.text = "OUT must be after IN."; return }
        status.text = "Saving\u2026"
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
