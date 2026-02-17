
# Contributing to LocalEdit

Thank you for your interest in contributing to LocalEdit! This project thrives on community involvement, and we welcome contributions of all kinds.

## 🌟 Ways to Contribute

### 1. Code Contributions
- Fix bugs
- Add new features
- Improve performance
- Refactor code for better maintainability

### 2. Translations
- Add new language files in `locales/`
- Improve existing translations
- Help with RTL language support

### 3. Documentation
- Improve user guides
- Add tutorials and examples
- Fix typos and clarify instructions
- Create video tutorials

### 4. Testing
- Report bugs with detailed reproduction steps
- Test on different operating systems
- Verify fixes and new features

### 5. Design
- Create icons and graphics
- Design UI improvements
- Make example projects

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Basic knowledge of Python and video processing

### Setup Development Environment

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/LocalEdit.git
   cd LocalEdit
Create a virtual environment
python -m venv venv

venv\Scripts\activate

source venv/bin/activate
Install dependencies
pip install -r Requirements.txt
Run LocalEdit
python Src/main.py
📝 Code Guidelines
Python Style
Follow PEP 8 style guide
Use meaningful variable and function names
Add docstrings to all functions and classes
Keep functions focused and small
Example:
def add_text_layer(self, text: str, position: tuple, duration: float) -> bool:
    """Add a text overlay to the timeline.
    
    Args:
        text: The text content to display
        position: (x, y) coordinates for placement
        duration: How long to show the text in seconds
    
    Returns:
        bool: True if successful, False otherwise
    """
    pass
Commits
Write clear, descriptive commit messages
Use present tense ("Add feature" not "Added feature")
Reference issue numbers when applicable
Good commit messages:
Add Arabic language support
Fix video export crash on Windows
Improve timeline performance for long projects
Update README with installation instructions
🌍 Adding Translations
We need your help making LocalEdit accessible worldwide!
Steps to Add a New Language:
Copy the English template
cp locales/en.json locales/YOUR_LANGUAGE_CODE.json
Translate all strings
Keep keys unchanged (e.g., "menu.file")
Translate only the values
Maintain formatting placeholders
Test the translation
python Src/main.py
Update language list
Add your language to Src/utils/locale_manager.py:
LANGUAGES = {
    'en': 'English',
    'es': 'Español',
    'YOUR_CODE': 'Your Language Name',
}
Submit a Pull Request
Translation Tips:
Keep translations concise (UI space is limited)
Use natural, conversational language
Test on actual UI to ensure it fits
For RTL languages (Arabic, Hebrew), add to RTL_LANGUAGES list
🐛 Reporting Bugs
Before Submitting:
Check if the bug has already been reported
Test with the latest version
Try to reproduce the bug consistently
Bug Report Should Include:
Operating System: Windows 10, macOS 13, Ubuntu 22.04, etc.
Python Version: python --version
LocalEdit Version: Check Help → About
Steps to Reproduce: Numbered list of exact steps
Expected Behavior: What should happen
Actual Behavior: What actually happens
Screenshots/Videos: If applicable
Error Messages: Full error text or logs
Example Bug Report:
**Bug:** Export fails when video has transparency

**OS:** Windows 11
**Python:** 3.11.5
**LocalEdit:** 0.1.0

**Steps:**
1. Add PNG image with transparency to Layer 1
2. Add audio to Layer 4
3. Click "Export Video"
4. Choose output location
5. Click OK

**Expected:** Video exports successfully
**Actual:** Error: "ValueError: Invalid alpha channel"

**Error Log:**
[Paste full error message here]
✨ Suggesting Features
We love new ideas! Before suggesting a feature:
Check existing issues - Maybe it's already planned
Consider the scope - Does it fit LocalEdit's philosophy?
Think about users - Who benefits and how?
Feature Request Template:
**Feature:** Short, descriptive title

**Problem:** What problem does this solve?

**Solution:** How would it work?

**Alternatives:** Other ways to solve this?

**Additional Context:** Screenshots, mockups, examples
🔄 Pull Request Process
Before Creating a PR:
Create a feature branch
git checkout -b feature/your-feature-name
Make your changes
Write clean, documented code
Test thoroughly
Update documentation if needed
Test your changes
python Src/main.py
Commit your changes
git add .
git commit -m "Add feature: your feature description"
Push to your fork
git push origin feature/your-feature-name
Creating the Pull Request:
Go to the original LocalEdit repository
Click "New Pull Request"
Select your fork and branch
Fill out the PR template:
**Description:**
Brief description of what this PR does

**Changes:**
- Added X feature
- Fixed Y bug
- Updated Z documentation

**Testing:**
How did you test these changes?

**Screenshots:**
If applicable, add screenshots

**Checklist:**
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
After Submitting:
Respond to review comments
Make requested changes
Be patient and respectful
🎯 Project Philosophy
LocalEdit is built on these principles:
1. Simplicity First
Don't add features "just because"
Keep the UI clean and uncluttered
Make common tasks easy
2. User Ownership
No cloud dependencies
No watermarks
No data collection
No forced updates
3. Privacy Matters
All processing happens locally
No telemetry or analytics
User files never leave their computer
4. Open and Free
Free forever, no premium tiers
Open source and transparent
Community-driven development
5. Global Accessibility
Support multiple languages
Work on all major platforms
Respect different workflows
When contributing, ask yourself:
Does this align with LocalEdit's values?
Does it add complexity or simplify?
Would I want to use this feature?
💬 Communication
GitHub Issues
Bug reports
Feature requests
Technical discussions
Pull Requests
Code reviews
Implementation discussions
Be Respectful
Assume good intentions
Give constructive feedback
Welcome newcomers
Celebrate contributions
🏆 Recognition
All contributors are valued and will be:
Listed in the project README
Credited in release notes
Celebrated in the community
Thank you for making LocalEdit better!
📄 License
By contributing to LocalEdit, you agree that your contributions will be licensed under the MIT License.
🙏 Questions?
If you have questions about contributing:
Open a GitHub issue with the "question" label
Describe what you want to contribute
Ask for guidance if needed
We're here to help! Contributing should be enjoyable and welcoming.
Baperebup! ✨
Remember: Every contribution, no matter how small, makes a difference. Thank you for being part of LocalEdit!
