package org.satdiva.localclip

import android.app.Activity
import android.app.AlertDialog
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.res.Configuration
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Outline
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.RectF
import android.graphics.drawable.ColorDrawable
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
import android.view.MotionEvent
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
import java.nio.ByteBuffer
import java.util.Locale
import kotlin.math.abs

/** Film-strip timeline: shows the video as thumbnails, the part that will be kept, and the playhead. */
class TimelineView(ctx: Context) : View(ctx) {
    var durationMs = 0L
    var inMs = 0L
    var outMs = 0L
    var posMs = 0L
    var frames: List<Bitmap> = emptyList()
    var touching = false
    var onScrub: (Long) -> Unit = {}
    var onInChanged: (Long) -> Unit = {}
    var onOutChanged: (Long) -> Unit = {}
    var onEdit: () -> Unit = {}

    private val d = ctx.resources.displayMetrics.density
    private val paint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val gold = Color.parseColor("#F5A623")
    private val teal = Color.parseColor("#2EC4B6")
    private var drag = 0

    override fun onMeasure(widthSpec: Int, heightSpec: Int) {
        setMeasuredDimension(View.MeasureSpec.getSize(widthSpec), (76 * d).toInt())
    }

    private fun xOf(ms: Long): Float =
        if (durationMs <= 0) 0f else (ms.toFloat() / durationMs.toFloat()) * width

    private fun msOf(x: Float): Long {
        if (width <= 0 || durationMs <= 0) return 0L
        val c = if (x < 0f) 0f else if (x > width.toFloat()) width.toFloat() else x
        return ((c / width.toFloat()) * durationMs.toFloat()).toLong()
    }

    override fun onDraw(c: Canvas) {
        val w = width.toFloat()
        val h = height.toFloat()
        paint.style = Paint.Style.FILL
        paint.color = Color.parseColor("#10151C")
        c.drawRect(0f, 0f, w, h, paint)

        if (frames.isNotEmpty()) {
            val cw = w / frames.size
            for (i in frames.indices) {
                val b = frames[i]
                val dst = RectF(i * cw, 0f, (i + 1) * cw, h)
                val ar = cw / h
                val bar = b.width.toFloat() / b.height.toFloat()
                val src: Rect
                if (bar > ar) {
                    val sw = (b.height * ar).toInt()
                    val x0 = (b.width - sw) / 2
                    src = Rect(x0, 0, x0 + sw, b.height)
                } else {
                    val sh = (b.width / ar).toInt()
                    val y0 = (b.height - sh) / 2
                    src = Rect(0, y0, b.width, y0 + sh)
                }
                c.drawBitmap(b, src, dst, null)
            }
        }

        if (durationMs > 0) {
            val xi = xOf(inMs)
            val xo = xOf(outMs)
            // dim what will NOT be kept
            paint.style = Paint.Style.FILL
            paint.color = Color.argb(185, 0, 0, 0)
            c.drawRect(0f, 0f, xi, h, paint)
            c.drawRect(xo, 0f, w, h, paint)
            // frame around what WILL be kept
            paint.style = Paint.Style.STROKE
            paint.strokeWidth = 3f * d
            paint.color = gold
            c.drawRect(xi, 1.5f * d, xo, h - 1.5f * d, paint)
            // handles
            paint.style = Paint.Style.FILL
            paint.color = teal
            c.drawRect(xi - 5f * d, 0f, xi + 5f * d, h, paint)
            paint.color = gold
            c.drawRect(xo - 5f * d, 0f, xo + 5f * d, h, paint)
            // playhead
            paint.color = Color.WHITE
            val xp = xOf(posMs)
            c.drawRect(xp - 1.5f * d, 0f, xp + 1.5f * d, h, paint)
        }
    }

    override fun onTouchEvent(e: MotionEvent): Boolean {
        if (durationMs <= 0) return true
        when (e.actionMasked) {
            MotionEvent.ACTION_DOWN -> {
                parent.requestDisallowInterceptTouchEvent(true)
                touching = true
                val di = abs(e.x - xOf(inMs))
                val dout = abs(e.x - xOf(outMs))
                val slop = 24f * d
                drag = if (di <= slop && di <= dout) 1 else if (dout <= slop) 2 else 3
                moveTo(e.x)
            }
            MotionEvent.ACTION_MOVE -> moveTo(e.x)
            MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                if (drag == 1 || drag == 2) onEdit()
                drag = 0
                touching = false
            }
        }
        return true
    }

    private fun moveTo(x: Float) {
        val ms = msOf(x)
        if (drag == 1) {
            val limit = if (outMs - 100 > 0) outMs - 100 else 0L
            inMs = if (ms > limit) limit else ms
            posMs = inMs
            onInChanged(inMs)
            onScrub(inMs)
        } else if (drag == 2) {
            val limit = if (inMs + 100 < durationMs) inMs + 100 else durationMs
            outMs = if (ms < limit) limit else ms
            posMs = outMs
            onOutChanged(outMs)
            onScrub(outMs)
        } else {
            posMs = ms
            onScrub(ms)
        }
        invalidate()
    }
}

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
        showSplash()
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

    // ---------- opening screen (clean, like any other app) ----------

    private fun showSplash() {
        val f = LinearLayout(this)
        f.orientation = LinearLayout.VERTICAL
        f.gravity = Gravity.CENTER
        f.setBackgroundColor(BG)

        val img = ImageView(this)
        img.scaleType = ImageView.ScaleType.FIT_CENTER
        img.setImageBitmap(bmp(Images.logoBig))
        img.clipToOutline = true
        img.outlineProvider = object : ViewOutlineProvider() {
            override fun getOutline(v: View, outline: Outline) {
                outline.setRoundRect(0, 0, v.width, v.height, dp(32).toFloat())
            }
        }
        f.addView(img, LinearLayout.LayoutParams(dp(160), dp(160)))

        val name = label("LocalClip", 34f, GOLD, true)
        name.gravity = Gravity.CENTER
        val nameLp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        nameLp.topMargin = dp(20)
        f.addView(name, nameLp)

        val tag = label("Lossless · Local · No recompression", 13f, DIM)
        tag.gravity = Gravity.CENTER
        f.addView(tag)

        val by = label("Made with love by Satdiva", 12f, DIM)
        by.gravity = Gravity.CENTER
        val byLp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        byLp.topMargin = dp(36)
        f.addView(by, byLp)

        f.setOnClickListener { goMain() }
        setContentView(f)
        ui.postDelayed({ goMain() }, 1400)
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
        logo.setImageBitmap(bmp(Images.logo))
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
        } else
