package org.satdiva.localclip

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.RectF
import android.view.MotionEvent
import android.view.View
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
