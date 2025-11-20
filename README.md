# Student Grading Management System

## 📋 Project Overview

A comprehensive Flask-based Student Grading Management System with support for multiple education levels (Primary, Secondary, Tertiary). Teachers can manage students, subjects, and grades with role-based functionality.

**Latest Update:** Multi-level education support implemented with full filtering and categorization.

---

## ✨ Features

### Core Features

- ✅ User authentication (teachers/admins)
- ✅ Student management
- ✅ Subject/Course management
- ✅ Grade recording and tracking
- ✅ Dashboard with statistics
- ✅ Real-time grade calculation

### NEW: Education Level Features

- ✅ Three education levels: Primary, Secondary, Tertiary
- ✅ Teacher assignment to education levels
- ✅ Student categorization by level
- ✅ Subject classification by level
- ✅ Advanced filtering by education level
- ✅ Level-specific statistics and reporting

### Advanced Features

- ✅ Search functionality
- ✅ Multiple quarter support (1st-4th)
- ✅ Automatic pass/fail determination
- ✅ Grade editing and history tracking
- ✅ Beautiful responsive UI with Tailwind CSS
- ✅ Mobile-friendly design

---

## 🚀 Quick Start

### Installation

1. **Clone or download the project**

```bash
cd Student\ Management
```

2. **Install dependencies**

```bash
pip install flask
```

3. **Run the application**

```bash
python app.py
```

4. **Access the application**

- Open browser and go to: `http://localhost:5000`

### First Time Setup

1. **Create account** (Sign Up)

   - Select your **Education Level** (Primary/Secondary/Tertiary)
   - Complete registration

2. **Add students**

   - Go to Students → Add New Student
   - Assign to your education level

3. **Add subjects**

   - Go to Subjects → Add New Subject
   - Select corresponding education level

4. **Record grades**
   - Go to Grades → Add New Grade
   - Enter student performance data
   - System auto-calculates final grades

---

## 📁 Project Structure

```
Student Management/
├── app.py                          # Main Flask application
├── grading_system.db              # SQLite database (auto-created)
├── static/
│   └── styles.css                 # Additional styles
├── templates/
│   ├── base.html                  # Base template
│   ├── index.html                 # Landing page
│   ├── login.html                 # Login page
│   ├── signup.html                # Sign up (with education level)
│   ├── dashboard.html             # Main dashboard
│   ├── students.html              # Student list (with level filter)
│   ├── add_student.html           # Add student form
│   ├── subjects.html              # Subject list
│   ├── add_subject.html           # Add subject form
│   ├── grades.html                # Grades list (with level filter)
│   ├── add_grade.html             # Add grade form
│   ├── edit_grade.html            # Edit grade form
│   └── about.html                 # About page
├── CHANGES_SUMMARY.md             # Technical documentation
├── TESTING_GUIDE.md               # Testing instructions
└── IMPLEMENTATION_COMPLETE.md     # Project completion summary
```

---

## 🎓 Education Levels

The system supports three education levels:

| Level        | Primary                    | Secondary                    | Tertiary                    |
| ------------ | -------------------------- | ---------------------------- | --------------------------- |
| **Type**     | Elementary                 | Middle & High                | University                  |
| **Grades**   | K-6                        | 7-12                         | Undergraduate+              |
| **Teachers** | Can manage Primary content | Can manage Secondary content | Can manage Tertiary content |
| **Color**    | Blue badge                 | Blue badge                   | Blue badge                  |

### How to Assign Education Levels

1. **Teachers:** Select during signup
2. **Students:** Select when adding student
3. **Subjects:** Select when adding subject

All records default to "Secondary" if not specified.

---

## 📊 Database Schema

### Users Table

```sql
- id (PRIMARY KEY)
- username (UNIQUE)
- email (UNIQUE)
- password (hashed)
- role (teacher/admin)
- education_level (Primary/Secondary/Tertiary)
- created_at
```

### Students Table

```sql
- id (PRIMARY KEY)
- student_id (UNIQUE)
- first_name
- last_name
- email (UNIQUE)
- section
- year_level
- education_level (Primary/Secondary/Tertiary)
- created_at
```

### Subjects Table

```sql
- id (PRIMARY KEY)
- subject_code (UNIQUE)
- subject_name
- description
- units
- education_level (Primary/Secondary/Tertiary)
- created_at
```

### Grades Table

```sql
- id (PRIMARY KEY)
- student_id (FOREIGN KEY)
- subject_id (FOREIGN KEY)
- quarter
- prelim (0-100)
- midterm (0-100)
- finals (0-100)
- final_grade (calculated)
- remarks (PASSED/FAILED)
- teacher_id (FOREIGN KEY)
- created_at
- updated_at
```

---

## 🔧 Configuration

### Security

- Secret key: Change in production
- Passwords: Hashed with werkzeug
- Sessions: Flask session management

### Database

- Type: SQLite3
- Location: `grading_system.db`
- Auto-created on first run

### Grading Rules

- **Final Grade Calculation:** (Prelim + Midterm + Finals) ÷ 3
- **Passing Score:** 75.00 or above
- **Failing Score:** Below 75.00

---

## 📝 Usage Examples

### Recording Grades

1. Click "Add New Grade"
2. Select Student and Subject
3. Choose Quarter (1st, 2nd, 3rd, or 4th)
4. Enter three component grades:
   - Prelim (0-100)
   - Midterm (0-100)
   - Finals (0-100)
5. System calculates final grade
6. Automatically determines Pass/Fail
7. Click Save Grade

### Filtering by Education Level

1. **Students Page:**

   - Use "All Education Levels" dropdown
   - Select Primary, Secondary, or Tertiary
   - View filtered student list

2. **Subjects Page:**

   - Check subject cards for education level badge
   - Filter mentally or search by name

3. **Grades Page:**
   - Use "All Levels" dropdown in filter bar
   - Select education level
   - View grades for that level

### Editing Grades

1. Go to Grades page
2. Click edit icon (pencil) on any grade
3. Update component grades
4. See live grade calculation
5. Click Save Changes

---

## 📖 Documentation Files

### CHANGES_SUMMARY.md

Complete technical documentation including:

- Database schema changes
- Backend route modifications
- Frontend template updates
- Code examples
- Migration instructions
- Benefits and future enhancements

### TESTING_GUIDE.md

Step-by-step testing procedures including:

- Test scenarios for each feature
- Expected behaviors
- Troubleshooting guide
- Testing checklist
- Database verification

### IMPLEMENTATION_COMPLETE.md

Project completion summary including:

- Overview of all changes
- Feature locations
- Usage scenarios
- Deployment instructions
- Quality assurance details

---

## 🐛 Troubleshooting

### Issue: Database won't create

**Solution:** Ensure `grading_system.db` file has write permissions

### Issue: Can't login

**Solution:** Check username/password are correct. Use signup to create account

### Issue: Education level not showing

**Solution:** Refresh the page, ensure it was selected before submission

### Issue: Grades not calculating

**Solution:** Ensure all three component grades (Prelim, Midterm, Finals) are entered

### Issue: Port 5000 already in use

**Solution:** Change port in app.py: `app.run(debug=True, port=5001)`

---

## 🔐 Security Notes

1. **Change the secret key in production**

   - In `app.py`: `app.secret_key = 'your-secret-key-change-this-in-production'`
   - Use a strong, random string

2. **Use HTTPS in production**

   - Enable SSL/TLS certificates
   - Use a production WSGI server (Gunicorn)

3. **Database backup**

   - Regularly backup `grading_system.db`
   - Store backups securely

4. **User authentication**
   - Passwords are hashed with werkzeug
   - Implement password reset in production

---

## 📱 Browser Compatibility

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## 🎨 User Interface

### Color Scheme

- **Primary Green:** #1f8f4a (Students, Primary actions)
- **Secondary Gold:** #d4b35a (Subjects)
- **Blue:** #3b82f6 (Grades, Education Level badges)
- **Light Gray:** Navigation and backgrounds

### Responsive Design

- Mobile-first approach
- Tablet optimized
- Desktop enhanced layout
- Adaptive navigation

---

## 📞 Support

For issues or questions:

1. Check TESTING_GUIDE.md for troubleshooting
2. Review CHANGES_SUMMARY.md for technical details
3. Check browser console for errors (F12)
4. Ensure database permissions are correct

---

## 📈 Future Enhancements

- [ ] Education level-specific dashboards
- [ ] Advanced reporting and analytics
- [ ] Export grades to PDF/Excel
- [ ] Parent portal for grade viewing
- [ ] SMS notifications for grades
- [ ] API endpoints for integration
- [ ] Multi-language support
- [ ] Advanced role-based access control

---

## 📄 License

This project is for educational purposes.

---

## 👨‍💼 About

**Student Grading Management System** - A modern, responsive web application for managing student grades across multiple education levels. Perfect for schools, universities, and educational institutions.

**Features:** Multi-level education support, real-time calculations, advanced filtering, responsive design.

---

## 🎯 Version Information

- **Version:** 2.0 (with Education Level Support)
- **Python:** 3.7+
- **Framework:** Flask
- **Database:** SQLite3
- **Last Updated:** November 19, 2025

---

**Status:** ✅ Production Ready

All features implemented, tested, and documented. Ready for deployment.
