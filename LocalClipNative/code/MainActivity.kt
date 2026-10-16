package org.satdiva.localclip

import android.content.res.Configuration
import android.graphics.Color
import android.graphics.Outline
import android.graphics.drawable.ColorDrawable
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.ViewOutlineProvider
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.VideoView

class MainActivity : PanelBuilder() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            window.setBackgroundDrawable(ColorDrawable(BG))
            window.statusBarColor = BG
            window.navigationBarColor = BG
            showSplash { goMain() }
        } catch (t: Throwable) {
            showError(t)
        }
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
        try {
            buildUi()
            kofiSometimes()
        } catch (t: Throwable) {
            showError(t)
        }
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

        val panel = buildPanel()

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
}
