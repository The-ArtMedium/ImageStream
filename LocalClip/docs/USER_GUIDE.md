# LocalClip User Guide

Welcome to LocalClip! This guide will help you trim videos quickly and efficiently.

## Quick Start

### 1. Import Video
- Click **📹 Import Video** button
- Or use keyboard: `Ctrl+O`
- Select your video file (MP4, AVI, MOV, MKV, WebM)

### 2. Navigate Timeline
- **Slider:** Drag to scrub through video
- **Play Button:** Click to play/pause
- **Keyboard:** `Space` to play/pause

### 3. Mark Your Clip
- **Scrub to start position**
- Click **📍 Mark Start** or press `I`
- **Scrub to end position**
- Click **📍 Mark End** or press `O`

### 4. Export
- Click **💾 Export Clip**
- Choose save location
- Wait for export to complete
- Done!

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+O` | Import video |
| `Space` | Play/Pause |
| `I` | Mark start (In point) |
| `O` | Mark end (Out point) |
| `Ctrl+Q` | Quit |

## Tips & Tricks

### Multiple Clips from One Video
1. Export first clip
2. Click **🔄 Reset Markers**
3. Mark new section
4. Export again
5. Repeat as needed

### Precise Trimming
- Use slider for approximate position
- Fine-tune by clicking near desired point
- Markers show exact times

### File Formats
- **Import:** MP4, AVI, MOV, MKV, WebM
- **Export:** MP4 (H.264, AAC audio)
- **Quality:** High bitrate (5000k) by default

## Workflow Example

### Scenario: Extract highlights from long recording

1. **Import** your 2-hour recording
2. **Mark** first highlight (5:30 - 7:45)
3. **Export** as `highlight_01.mp4`
4. **Reset markers**
5. **Mark** second highlight (23:10 - 25:30)
6. **Export** as `highlight_02.mp4`
7. Repeat for all highlights

Result: Multiple short clips ready to use in LocalEdit or share directly!

## Best Practices

### Before You Start
- Know which sections you want to extract
- Write down timestamps if helpful
- Have export folder ready

### During Export
- Don't close LocalClip while exporting
- Longer clips take more time
- Progress bar shows render status

### File Management
- Name clips descriptively
- Organize by project/date
- Keep originals separate from exports

## Troubleshooting

### Video Won't Load
- Check file format is supported
- Verify file isn't corrupted
- Try converting with FFmpeg first

### Export Takes Too Long
- Longer clips take more time
- Normal: 1-5x real-time duration
- Close other applications for faster export

### Can't Mark Points
- Ensure video is loaded first
- Check if slider is enabled
- Try restarting LocalClip

### Quality Issues
- LocalClip uses high bitrate (5000k)
- No quality loss from trimming
- Original video quality is preserved

## Advanced Usage

### Command Line (Future)
```bash
# Future feature - CLI trimming
localclip trim input.mp4 --start 00:05:30 --end 00:07:45 --output clip.mp4
```

### Batch Processing (Future)
- Import multiple videos
- Set markers for each
- Export all at once

### Custom Export Settings (Future)
- Adjust bitrate
- Choose codec
- Set resolution

## Integration with LocalEdit

**Perfect Workflow:**

1. **LocalClip:** Trim raw footage into clips
2. **LocalEdit:** Assemble clips into final video
3. Add music, text, graphics in LocalEdit
4. Export complete project

**Example:**
```
Raw footage (30min) → LocalClip
  ├─ clip1.mp4 (2min)
  ├─ clip2.mp4 (1.5min)
  └─ clip3.mp4 (3min)
       ↓
  LocalEdit assembly
       ↓
  Final video with music & text
```

## Performance Tips

### For Smooth Operation
- Close preview apps during export
- Use SSD for faster I/O
- 8GB+ RAM recommended for large files

### For Large Files
- Trim to smaller chunks first
- Export progressively rather than all at once
- Monitor disk space

## FAQ

**Q: Does LocalClip compress my video?**
A: No. High bitrate export preserves quality. Only trimming, no re-encoding quality loss.

**Q: Can I undo a trim?**
A: Original file is never modified. Your source video is safe.

**Q: How many clips can I export?**
A: Unlimited. No restrictions.

**Q: Does it work offline?**
A: Yes! Completely offline. No internet needed.

**Q: Is there a file size limit?**
A: No limits. Only constrained by your computer's resources.

**Q: Can I trim multiple videos at once?**
A: Not yet. One video at a time. Batch processing coming in future version.

## Getting Help

- **GitHub Issues:** Report bugs or request features
- **Documentation:** Check README.md for updates
- **Community:** Share tips with other users

## Future Features

Coming in future versions:
- Video preview window
- Frame-by-frame navigation
- Batch processing
- Custom export presets
- Transition effects
- Audio waveform display

---

**Remember:** LocalClip does one thing perfectly - trim videos. For multi-clip assembly, use LocalEdit!

**Simple. Local. Yours.**

**Baperebup!** ✨

