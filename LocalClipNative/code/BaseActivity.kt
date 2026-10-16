package org.satdiva.localclip

import android.app.Activity
import android.app.AlertDialog
import android.content.Intent
import android.graphics.Color
import android.graphics.Outline
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Handler
import android.os.Looper
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.ViewOutlineProvider
import android.widget.Button
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import java.util.Locale

/** Colours, small view helpers, the opening screen and the Ko-fi messages. */
abstract class BaseActivity : Activity() {

    protected val BG = Color.parseColor("#0B0F14")
    protected val PANEL = Color.parseColor("#18202A")
    protected val GOLD = Color.parseColor("#F5A623")
    protected val TEAL = Color.parseColor("#2EC4B6")
    protected val DIM = Color.parseColor("#9AA7B4")
    protected val KEY = Color.parseColor("#2A3441")
    private val KOFI_URL = "https://ko-fi.com/1satdiva"

    protected val ui = Handler(Looper.getMainLooper())

    protected fun dp(v: Int): Int = (v * resources.displayMetrics.density).toInt()

    protected fun pill(label: String, bg: Int, fg: Int, small: Boolean = false, onClick: () -> Unit): Button {
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

    protected fun row(vararg views: View): LinearLayout {
        val r = LinearLayout(this)
        r.orientation = LinearLayout.HORIZONTAL
        for (v in views) {
            val lp = LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f)
            lp.setMargins(dp(3), dp(3), dp(3), dp(3))
            r.addView(v, lp)
        }
        return r
    }

    protected fun label(text: String, size: Float, color: Int, bold: Boolean = false): TextView {
        val t = TextView(this)
        t.text = text
        t.textSize = size
        t.setTextColor(color)
        if (bold) t.setTypeface(t.typeface, android.graphics.Typeface.BOLD)
        return t
    }

    protected fun openKofi() {
        try {
            startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(KOFI_URL)))
        } catch (e: Exception) { /* no browser available */ }
    }

    protected fun kofiButton(): Button {
        val b = pill("☕ Ko-fi", GOLD, Color.BLACK) { openKofi() }
        b.minHeight = dp(40)
        b.minimumHeight = dp(40)
        b.textSize = 14f
        return b
    }

    /** mm:ss.mmm */
    protected fun fmt(ms: Long): String {
        val m = if (ms < 0) 0L else ms
        val total = m / 1000
        return String.format(Locale.US, "%02d:%02d.%03d", total / 60, total % 60, m % 1000)
    }

    protected fun showSplash(onDone: () -> Unit) {
        val f = LinearLayout(this)
        f.orientation = LinearLayout.VERTICAL
        f.gravity = Gravity.CENTER
        f.setBackgroundColor(BG)

        val img = ImageView(this)
        img.scaleType = ImageView.ScaleType.FIT_CENTER
        img.setImageResource(R.mipmap.ic_launcher)
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

        val tag = label("Lossless \u00B7 Local \u00B7 No recompression", 13f, DIM)
        tag.gravity = Gravity.CENTER
        f.addView(tag)

        val by = label("Made with love by Satdiva", 12f, DIM)
        by.gravity = Gravity.CENTER
        val byLp = LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        byLp.topMargin = dp(36)
        f.addView(by, byLp)

        f.setOnClickListener { onDone() }
        setContentView(f)
        ui.postDelayed({ onDone() }, 1400)
    }

    protected fun kofiSometimes() {
        val p = getSharedPreferences("lc", MODE_PRIVATE)
        val n = p.getInt("launches", 0) + 1
        p.edit().putInt("launches", n).apply()
        if (!(n == 2 || n % 5 == 0)) return
        val messages = arrayOf(
            "LocalClip is free, private and works offline. It is made by one independent artist. " +
                "If it saves you time, a coffee on Ko-fi helps keep it going. Thank you for being here.",
            "No ads. No tracking. No subscriptions. Just a tool made with care. " +
                "If it is useful to you, you can say thanks with a coffee on Ko-fi.",
            "Every clip you cut stays on your phone. If LocalClip helps your work, " +
                "a small coffee on Ko-fi keeps new tools coming. Thank you!"
        )
        AlertDialog.Builder(this)
            .setTitle("A little thank you \u2615")
            .setMessage(messages[n % messages.size])
            .setPositiveButton("Visit Ko-fi") { _, _ -> openKofi() }
            .setNegativeButton("Maybe later", null)
            .show()
    }
}
