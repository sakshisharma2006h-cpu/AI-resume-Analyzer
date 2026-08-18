// ==========================================
// AI RESUME ANALYZER - SCRIPT.JS
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("✅ AI Resume Analyzer Loaded");


    // ==========================================
    // DOM ELEMENTS
    // ==========================================

    const uploadZone =
        document.getElementById("uploadZone");

    const fileInput =
        document.getElementById("fileInput");

    const fileBadge =
        document.getElementById("fileBadge");

    const uploadTitle =
        document.getElementById("uploadTitle");

    const uploadText =
        document.getElementById("uploadText");

    const analyzeBtn =
        document.getElementById("analyzeBtn");

    const jobRoleInput =
        document.getElementById("jobRole");

    const loader =
        document.getElementById("loader");

    const loaderText =
        document.getElementById("loaderText");

    const scoreElement =
        document.getElementById("scoreElement");

    const scoreCircle =
        document.getElementById("scoreCircle");

    const scoreTitle =
        document.getElementById("scoreTitle");

    const scoreDescription =
        document.getElementById("scoreDescription");

    const gradeElement =
        document.getElementById("gradeElement");

    const foundSkills =
        document.getElementById("foundSkills");

    const missingSkills =
        document.getElementById("missingSkills");

    const keywordProgress =
        document.getElementById("keywordProgress");

    const structureProgress =
        document.getElementById("structureProgress");

    const formatProgress =
        document.getElementById("formatProgress");

    const keywordValue =
        document.getElementById("keywordValue");

    const structureValue =
        document.getElementById("structureValue");

    const formatValue =
        document.getElementById("formatValue");

    const resumePreview =
        document.getElementById("resumePreview");

    const downloadBtn =
        document.getElementById("downloadBtn");


    // ==========================================
    // CHECK ELEMENTS
    // ==========================================

    if (
        !uploadZone ||
        !fileInput ||
        !analyzeBtn ||
        !jobRoleInput
    ) {

        console.error(
            "❌ Required HTML elements are missing."
        );

        return;

    }


    console.log(
        "✅ All required elements found"
    );


    // ==========================================
    // UPLOAD ZONE CLICK
    // ==========================================

    uploadZone.addEventListener(
        "click",
        function () {

            fileInput.click();

        }
    );


    // ==========================================
    // FILE SELECT
    // ==========================================

    fileInput.addEventListener(
        "change",
        function () {

            const file =
                fileInput.files[0];

            if (file) {

                handleFile(file);

            }

        }
    );


    // ==========================================
    // DRAG OVER
    // ==========================================

    uploadZone.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            uploadZone.classList.add("drag");

        }
    );


    // ==========================================
    // DRAG LEAVE
    // ==========================================

    uploadZone.addEventListener(
        "dragleave",
        function () {

            uploadZone.classList.remove("drag");

        }
    );


    // ==========================================
    // DROP
    // ==========================================

    uploadZone.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            uploadZone.classList.remove("drag");

            const file =
                event.dataTransfer.files[0];

            if (file) {

                handleFile(file);

            }

        }
    );


    // ==========================================
    // HANDLE FILE
    // ==========================================

    function handleFile(file) {

        const fileName =
            file.name.toLowerCase();


        const allowedExtensions = [
            ".pdf",
            ".doc",
            ".docx"
        ];


        const validExtension =
            allowedExtensions.some(
                function (extension) {

                    return fileName.endsWith(
                        extension
                    );

                }
            );


        if (!validExtension) {

            alert(
                "❌ Please upload PDF, DOC or DOCX file."
            );

            fileInput.value = "";

            return;

        }


        // Maximum 5MB

        if (file.size > 5 * 1024 * 1024) {

            alert(
                "❌ File size must be less than 5MB."
            );

            fileInput.value = "";

            return;

        }


        // Update UI

        fileBadge.textContent =
            "📄 " + file.name;


        uploadTitle.textContent =
            "Resume Selected ✓";


        uploadText.textContent =
            "Click Analyze Resume to continue.";


        console.log(
            "✅ Selected:",
            file.name
        );

    }


    // ==========================================
    // ANALYZE BUTTON
    // ==========================================

    analyzeBtn.addEventListener(
        "click",
        function () {

            // Check file

            if (
                !fileInput.files ||
                fileInput.files.length === 0
            ) {

                alert(
                    "⚠️ Please upload your resume first."
                );

                return;

            }


            // Check job role

            const jobRole =
                jobRoleInput.value.trim();


            if (jobRole === "") {

                alert(
                    "⚠️ Please enter Target Job Role."
                );

                jobRoleInput.focus();

                return;

            }


            console.log(
                "🔍 Starting analysis..."
            );


            startAnalysis(jobRole);

        }
    );


    // ==========================================
    // START ANALYSIS
    // ==========================================

    function startAnalysis(jobRole) {

        loader.style.display = "flex";

        analyzeBtn.disabled = true;

        analyzeBtn.textContent =
            "Analyzing...";


        const messages = [
            "Reading resume...",
            "Extracting skills...",
            "Checking keywords...",
            "Analyzing experience...",
            "Calculating ATS score..."
        ];


        let index = 0;


        loaderText.textContent =
            messages[0];


        const interval =
            setInterval(function () {

                index++;


                if (index < messages.length) {

                    loaderText.textContent =
                        messages[index];

                }

            }, 600);


        setTimeout(function () {

            clearInterval(interval);

            loader.style.display = "none";

            generateResult(jobRole);

        }, 3200);

    }


    // ==========================================
    // GENERATE RESULT
    // ==========================================

    function generateResult(jobRole) {

        // Demo ATS score

        const score = 85;


        updateScore(score);

        updateSkills();

        updateProgress();

        updateGrade(score);

        updateDescription(
            score,
            jobRole
        );


        analyzeBtn.disabled = false;

        analyzeBtn.textContent =
            "Analysis Complete ✓";


        console.log(
            "✅ Analysis complete"
        );


        // Scroll to score

        document
            .getElementById("resultSection")
            .scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

    }


    // ==========================================
    // UPDATE SCORE
    // ==========================================

    function updateScore(score) {

        scoreElement.textContent =
            score + "%";


        const degree =
            score * 3.6;


        scoreCircle.style.background =
            `conic-gradient(
                #6366f1 0deg,
                #6366f1 ${degree}deg,
                #e2e8f0 ${degree}deg,
                #e2e8f0 360deg
            )`;

    }


    // ==========================================
    // UPDATE SKILLS
    // ==========================================

    function updateSkills() {

        const detected = [
            "Java",
            "Spring Boot",
            "React",
            "MySQL",
            "MongoDB"
        ];


        const missing = [
            "Python",
            "Docker",
            "Kubernetes"
        ];


        foundSkills.innerHTML = "";

        missingSkills.innerHTML = "";


        detected.forEach(
            function (skill) {

                const tag =
                    document.createElement("div");

                tag.className =
                    "tag tag-found";

                tag.textContent =
                    skill;

                foundSkills.appendChild(tag);

            }
        );


        missing.forEach(
            function (skill) {

                const tag =
                    document.createElement("div");

                tag.className =
                    "tag tag-missing";

                tag.textContent =
                    skill;

                missingSkills.appendChild(tag);

            }
        );

    }


    // ==========================================
    // UPDATE PROGRESS
    // ==========================================

    function updateProgress() {

        const keyword = 85;

        const structure = 95;

        const formatting = 88;


        keywordProgress.style.width =
            keyword + "%";

        structureProgress.style.width =
            structure + "%";

        formatProgress.style.width =
            formatting + "%";


        keywordValue.textContent =
            keyword + "%";

        structureValue.textContent =
            structure + "%";

        formatValue.textContent =
            formatting + "%";

    }


    // ==========================================
    // UPDATE GRADE
    // ==========================================

    function updateGrade(score) {

        if (score >= 90) {

            gradeElement.textContent =
                "Grade: A+";

        }
        else if (score >= 80) {

            gradeElement.textContent =
                "Grade: A";

        }
        else if (score >= 70) {

            gradeElement.textContent =
                "Grade: B";

        }
        else if (score >= 60) {

            gradeElement.textContent =
                "Grade: C";

        }
        else {

            gradeElement.textContent =
                "Grade: D";

        }

    }


    // ==========================================
    // UPDATE DESCRIPTION
    // ==========================================

    function updateDescription(
        score,
        jobRole
    ) {

        scoreTitle.textContent =
            "Excellent ATS Compatibility";


        scoreDescription.textContent =
            `Your resume has an ATS score of ${score}% for the ${jobRole} role. Add the missing keywords and improve measurable achievements to make it stronger.`;

    }


    // ==========================================
    // RESUME PREVIEW
    // ==========================================

    fileInput.addEventListener(
        "change",
        function () {

            const file =
                fileInput.files[0];

            if (!file) {
                return;
            }


            resumePreview.innerHTML = `

                <h2>
                    ${escapeHTML(file.name)}
                </h2>

                <p>
                    Resume uploaded successfully.
                </p>

                <p>
                    File type:
                    ${escapeHTML(file.type || "Document")}
                </p>

                <p>
                    File size:
                    ${(file.size / 1024).toFixed(2)} KB
                </p>

            `;

        }
    );


    // ==========================================
    // ESCAPE HTML
    // ==========================================

    function escapeHTML(text) {

        const div =
            document.createElement("div");

        div.textContent = text;

        return div.innerHTML;

    }


    // ==========================================
    // DOWNLOAD REPORT
    // ==========================================

    downloadBtn.addEventListener(
        "click",
        function () {

            const score =
                scoreElement.textContent;


            const role =
                jobRoleInput.value ||
                "Not specified";


            const report =

`AI RESUME ANALYZER
===========================

Target Job Role:
${role}

ATS Score:
${score}

Grade:
${gradeElement.textContent}

Detected Skills:
Java, Spring Boot, React, MySQL, MongoDB

Missing Keywords:
Python, Docker, Kubernetes

ATS Compatibility:
Keyword Match: 85%
Section Structure: 95%
Resume Formatting: 88%

Suggestions:
1. Add measurable achievements.
2. Add relevant job keywords.
3. Include relevant cloud/container technologies.

===========================
Generated by AI Resume Analyzer`;


            const blob =
                new Blob(
                    [report],
                    {
                        type: "text/plain"
                    }
                );


            const url =
                URL.createObjectURL(blob);


            const link =
                document.createElement("a");


            link.href = url;

            link.download =
                "ATS-Resume-Report.txt";


            link.click();


            URL.revokeObjectURL(url);

        }
    );

});