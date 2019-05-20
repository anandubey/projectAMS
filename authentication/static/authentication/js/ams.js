function toggleDisplayFaculty() {
    var faculty = document.getElementById("faculty");
    var student = document.getElementById("student");
    if (faculty.style.display === "none") {
        faculty.style.display = "block";
        student.style.display = "none";
    }
    else {
        faculty.style.display = "block";
        student.style.display = "none";
     }
}

function toggleDisplayStudent() {
    var student = document.getElementById("student");
    var faculty = document.getElementById("faculty");
    if (student.style.display === "none") {
        student.style.display = "block";
        faculty.style.display = "none";
    }
    else {
        student.style.display = "block";
        faculty.style.display = "none";
    }
}