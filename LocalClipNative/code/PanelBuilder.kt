package org.satdiva.localclip

import android.graphics.Color
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.widget.LinearLayout

/** Builds the controls panel (buttons, texts). */
abstract class PanelBuilder : EditorLogic() {

    fun buildPanel(): LinearLayout {
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
        return panel
    }
}
