import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Button,
  Box,
  Snackbar,
  Alert,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Grid,
  Tooltip,
} from "@mui/material";
import AddPhotoAlternateIcon from "@mui/icons-material/AddPhotoAlternate";
import UpdateIcon from "@mui/icons-material/Update";
import DownloadIcon from "@mui/icons-material/Download";
import RestartAltIcon from "@mui/icons-material/RestartAlt";

function App() {
  const [photos, setPhotos] = useState([]);
  const [attendance, setAttendance] = useState([]);
  const [mode, setMode] = useState("capture");
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });
  const webcamRef = useRef();

  // Use your LAN IP if you want to share with others on same network
  const backendURL = "http://localhost:5000";

  const showSnackbar = (message, severity = "success") =>
    setSnackbar({ open: true, message, severity });

  const capturePhoto = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    try {
      const resp = await fetch(`${backendURL}/upload_photo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: imageSrc }),
      });
      const result = await resp.json();
      setPhotos((prev) => [...prev, result.filename]);
      showSnackbar("Photo captured!", "success");
    } catch (e) {
      showSnackbar("Error capturing photo!", "error");
    }
  };

  const analyzeAttendance = async () => {
    try {
      const resp = await fetch(`${backendURL}/analyze_attendance`);
      const result = await resp.json();
      setAttendance(result.attendance);
      setMode("result");
      showSnackbar("Attendance analyzed!", "success");
    } catch (e) {
      showSnackbar("Failed to analyze attendance!", "error");
    }
  };

  // Manual override: Mark Present
  const markPresent = (index) => {
    setAttendance((attendance) =>
      attendance.map((row, i) =>
        i === index ? { ...row, attendance: "Present" } : row
      )
    );
    showSnackbar("Student marked present!", "info");
  };

  // Manual override: Mark Absent
  const markAbsent = (index) => {
    setAttendance((attendance) =>
      attendance.map((row, i) =>
        i === index ? { ...row, attendance: "Absent" } : row
      )
    );
    showSnackbar("Student marked absent!", "info");
  };

  // Sync attendance to backend and download CSV
  const syncAttendance = async () => {
    try {
      await fetch(`${backendURL}/update_attendance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ attendance }),
      });
      window.open(`${backendURL}/download_csv`);
      showSnackbar("Attendance CSV downloaded!", "success");
    } catch (e) {
      showSnackbar("Download failed!", "error");
    }
  };

  const resetSession = async () => {
    try {
      await fetch(`${backendURL}/reset_photos`, { method: "POST" });
      setPhotos([]);
      setAttendance([]);
      setMode("capture");
      showSnackbar("Session reset!", "success");
    } catch (e) {
      showSnackbar("Could not reset!", "error");
    }
  };

  return (
    <>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Face Recognition Attendance
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        {mode === "capture" ? (
          <Box sx={{ textAlign: "center" }}>
            <Webcam audio={false} ref={webcamRef} screenshotFormat="image/jpeg" style={{ marginBottom: "1em" }} />
            <Grid container spacing={2} justifyContent="center" sx={{ mb: 2 }}>
              <Grid item>
                <Tooltip title="Capture classroom photo">
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<AddPhotoAlternateIcon />}
                    onClick={capturePhoto}
                  >
                    Capture Photo
                  </Button>
                </Tooltip>
              </Grid>
              <Grid item>
                <Tooltip title="Analyze attendance">
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<UpdateIcon />}
                    onClick={analyzeAttendance}
                    disabled={photos.length === 0}
                  >
                    Finish & Analyze
                  </Button>
                </Tooltip>
              </Grid>
              <Grid item>
                <Tooltip title="Reset session">
                  <Button
                    variant="outlined"
                    color="secondary"
                    startIcon={<RestartAltIcon />}
                    onClick={resetSession}
                  >
                    Reset
                  </Button>
                </Tooltip>
              </Grid>
            </Grid>
            <Typography variant="body2">
              {photos.length} classroom photo{photos.length !== 1 ? "s" : ""} captured.
            </Typography>
          </Box>
        ) : (
          <>
            <Typography variant="h5" sx={{ mb: 2 }}>
              Attendance Result
            </Typography>
            <TableContainer component={Paper} sx={{ mb: 2 }}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Attendance</TableCell>
                    <TableCell>Action</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendance.map((row, i) => (
                    <TableRow key={i}>
                      <TableCell>{row.name}</TableCell>
                      <TableCell>{row.attendance}</TableCell>
                      <TableCell>
                        {row.attendance === "Absent" ? (
                          <Tooltip title="Mark as present">
                            <Button
                              variant="contained"
                              color="primary"
                              onClick={() => markPresent(i)}
                              sx={{ mr: 1 }}
                            >
                              Mark Present
                            </Button>
                          </Tooltip>
                        ) : (
                          <Tooltip title="Mark as absent">
                            <Button
                              variant="contained"
                              color="secondary"
                              onClick={() => markAbsent(i)}
                            >
                              Mark Absent
                            </Button>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item>
                <Tooltip title="Download attendance CSV">
                  <Button
                    variant="contained"
                    color="success"
                    startIcon={<DownloadIcon />}
                    onClick={syncAttendance}
                  >
                    Download Attendance CSV
                  </Button>
                </Tooltip>
              </Grid>
              <Grid item>
                <Tooltip title="New session">
                  <Button
                    variant="outlined"
                    color="secondary"
                    startIcon={<RestartAltIcon />}
                    onClick={resetSession}
                  >
                    New Session
                  </Button>
                </Tooltip>
              </Grid>
            </Grid>
          </>
        )}
      </Container>
      <Box component="footer" textAlign="center" my={3}>
        <Typography variant="body2" color="text.secondary">
          © 2025 Face Recognition Attendance App
        </Typography>
      </Box>
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}

export default App;
