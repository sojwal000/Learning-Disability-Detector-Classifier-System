# 🚀 Quick Start Guide

## Learning Disability Detector & Classifier System

This guide will get you up and running in **under 15 minutes**!

---

## ⚡ Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Python 3.10+** installed ([Download](https://www.python.org/downloads/))
- [ ] **Node.js 18+** installed ([Download](https://nodejs.org/))
- [ ] **PostgreSQL 14+** installed ([Download](https://www.postgresql.org/download/))
- [ ] **Git** installed (optional, for version control)

Check your installations:

```powershell
python --version    # Should show Python 3.10 or higher
node --version      # Should show v18 or higher
psql --version      # Should show PostgreSQL 14 or higher
```

---

## 📦 Step 1: Database Setup (5 minutes)

### Create Database

Open PostgreSQL command line or pgAdmin and run:

```sql
-- Create database
CREATE DATABASE ld_detector;

-- Create user (optional, or use your existing user)
CREATE USER ld_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ld_detector TO ld_user;
```

**Note**: Remember your database credentials for the next step!

---

## ⚙️ Step 2: Automated Setup (5 minutes)

### Run Setup Script

Open PowerShell in the project directory and run:

```powershell
# Navigate to project directory
cd "c:\Users\Swastik\Desktop\ClientProjects\LDD&CS"

# Run setup script
.\setup.ps1
```

This script will:

- ✅ Check Python and Node.js installations
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Install all Node.js dependencies
- ✅ Create storage directories
- ✅ Create .env configuration file

---

## 🔧 Step 3: Configuration (2 minutes)

### Edit Environment Variables

Open `backend\.env` in your text editor and update:

```env
DATABASE_URL=postgresql://ld_user:your_secure_password@localhost:5432/ld_detector
SECRET_KEY=run-this-command-to-generate
```

### Generate Secret Key

Run this command in PowerShell:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste it as your `SECRET_KEY` in `.env`

### Initialize Database

```powershell
cd backend
.\init_database.ps1
```

---

## 🎬 Step 4: Start the Application (3 minutes)

### Start Backend Server

**Terminal 1** - Backend:

```powershell
cd backend
.\start.ps1
```

You should see:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Start Frontend Server

**Terminal 2** - Frontend (new terminal):

```powershell
cd frontend
.\start.ps1
```

You should see:

```
  VITE ready in XXX ms
  ➜  Local:   http://localhost:3000/
```

---

## 🎉 Step 5: Access the Application

### URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### First Time Setup

1. **Register Admin Account**

   - Go to http://localhost:3000/register
   - Fill in the form:
     - Full Name: `Admin User`
     - Username: `admin`
     - Email: `admin@example.com`
     - Role: `Administrator`
     - Password: `SecurePassword123` (change this!)
   - Click "Register"

2. **Login**

   - You'll be redirected to login page
   - Enter username: `admin`
   - Enter password: `SecurePassword123`
   - Click "Sign In"

3. **You're In!** 🎊
   - You should now see the Dashboard

---

## 📝 Step 6: Test the System (Optional)

### Quick Test Workflow

1. **Add a Student**

   - Click "Students" in navigation
   - Click "+ Add Student"
   - Fill in student details
   - Click "Add Student"

2. **Submit a Test**

   - Click "Submit Test" in navigation
   - Select the student you just created
   - Choose "Reading Test"
   - Fill in sample data:
     - Text Provided: `The quick brown fox jumps over the lazy dog`
     - Text Read: `The qick brown fox jmps over the lzy dog`
     - Time Taken: `30` seconds
   - Click "Submit Test"

3. **View Results**

   - Click "Students" → Select your student
   - View the test results and analytics
   - Check the automatically generated ML prediction

4. **Generate Report**
   - Click "Reports" in navigation
   - Select the student
   - Click "Generate New Report"
   - Download the generated report

---

## 🛠️ Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError`

```powershell
# Reinstall dependencies
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Error**: `Connection refused` (Database)

- Check PostgreSQL is running: `Services.msc` (Windows)
- Verify database credentials in `backend\.env`
- Ensure database exists: `psql -U postgres -l`

### Frontend Won't Start

**Error**: `Cannot find module`

```powershell
# Reinstall dependencies
cd frontend
Remove-Item node_modules -Recurse -Force
npm install
```

**Error**: `Port 3000 is already in use`

```powershell
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

### Can't Login

- Check backend is running on port 8000
- Check browser console for errors (F12)
- Verify database has user records: `SELECT * FROM users;`

---

## 📖 Next Steps

### Learn More

- Read the full [README.md](README.md) for detailed information
- Check [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for architecture details
- Explore API documentation at http://localhost:8000/docs

### Customize

- Modify colors in `frontend/src/index.css`
- Add more test types in backend
- Enhance ML models with your data
- Create custom reports

### Deploy

- See README.md for production deployment guide
- Consider hosting on:
  - Backend: Heroku, DigitalOcean, AWS EC2
  - Frontend: Vercel, Netlify, AWS S3 + CloudFront
  - Database: AWS RDS, DigitalOcean Managed Database

---

## 🎯 Common Use Cases

### For Teachers

1. **Daily Testing**

   - Students → Add Student
   - Submit Test → Fill test data
   - View student detail page for results

2. **Progress Monitoring**

   - Dashboard → View recent activity
   - Students → Click student → View analytics
   - Track improvement over time

3. **Parent Communication**
   - Reports → Generate report
   - Download → Share with parents
   - Use recommendations for IEP planning

### For Administrators

1. **System Overview**

   - Dashboard → View system-wide statistics
   - Analytics → See trends
   - Monitor teacher usage

2. **User Management**
   - Register new teacher accounts
   - Monitor system activity
   - Review audit logs (future feature)

---

## ⚡ Pro Tips

1. **Keyboard Shortcuts**

   - `Ctrl + K` in browser to open dev tools
   - Watch Network tab for API calls
   - Use Redux DevTools (if added)

2. **Development**

   - Both servers support hot-reload
   - Changes auto-update without restart
   - Check terminal for errors

3. **Data Entry**

   - Copy-paste sample test data
   - Use consistent naming for students
   - Add meaningful notes in forms

4. **Performance**
   - Close unused browser tabs
   - Restart servers daily
   - Clear browser cache if needed

---

## 🆘 Getting Help

### Resources

- **Documentation**: Check README.md and PROJECT_OVERVIEW.md
- **API Docs**: http://localhost:8000/docs
- **Logs**: Check terminal output for errors

### Support

If you encounter issues:

1. Check troubleshooting section above
2. Review error messages carefully
3. Search error message online
4. Contact: support@lddetector.com

---

## ✅ Success Checklist

Before marking setup as complete:

- [ ] Backend starts without errors
- [ ] Frontend loads at localhost:3000
- [ ] Can register and login
- [ ] Can add a student
- [ ] Can submit a test
- [ ] Can view analytics
- [ ] Can generate a report

---

**Congratulations! 🎉**

You now have a fully functional Learning Disability Detector & Classifier System!

Start exploring the features and customizing it to your needs.

---

**Quick Start Version**: 1.0  
**Last Updated**: November 2024
