const API_URL = "https://ai-pdf-llm.onrender.com";


const pdfInput =
    document.getElementById("pdfFile");


const dropZone =
    document.getElementById("dropZone");


const selectedFile =
    document.getElementById("selectedFile");



/* FILE SELECTION */


pdfInput.addEventListener(
    "change",
    function () {

        if (this.files.length > 0) {

            selectedFile.textContent =
                "Selected: " + this.files[0].name;

        }

    }
);



/* DRAG & DROP */


dropZone.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        dropZone.style.borderColor =
            "#7c5cff";

    }
);


dropZone.addEventListener(
    "dragleave",
    function () {

        dropZone.style.borderColor =
            "";

    }
);


dropZone.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();

        dropZone.style.borderColor =
            "";

        if (event.dataTransfer.files.length > 0) {

            pdfInput.files =
                event.dataTransfer.files;

            selectedFile.textContent =
                "Selected: " +
                event.dataTransfer.files[0].name;

        }

    }
);



/* UPLOAD PDF */


async function uploadPDF() {

    const status =
        document.getElementById("uploadStatus");


    if (!pdfInput.files.length) {

        status.textContent =
            "Please choose a PDF first.";

        return;

    }


    const formData =
        new FormData();


    formData.append(
        "file",
        pdfInput.files[0]
    );


    status.textContent =
        "⏳ Analyzing your PDF...";


    try {

        const response =
            await fetch(
                `${API_URL}/upload`,
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            status.textContent =
                data.error ||
                "PDF analysis failed.";

            return;

        }


        status.textContent =
            `✓ PDF analyzed successfully — ${data.chunks} knowledge chunks created.`;

    }

    catch (error) {

        console.error(error);

        status.textContent =
            "Backend connection failed. Make sure FastAPI is running.";

    }

}



/* ASK AI */


async function askQuestion() {

    const input =
        document.getElementById("question");


    const answer =
        document.getElementById("answer");


    const question =
        input.value.trim();


    if (!question) {

        answer.innerHTML =
            `<span class="empty-text">
                Please enter a question.
            </span>`;

        return;

    }


    answer.textContent =
        "✦ AI is thinking...";


    try {

        const response =
            await fetch(
                `${API_URL}/ask?question=${encodeURIComponent(question)}`,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            answer.textContent =
                data.error ||
                "Unable to answer.";

            return;

        }


        answer.textContent =
            data.answer;

    }

    catch (error) {

    console.error("ASK ERROR:", error);

    answer.textContent =
        "AI Error: " + error.message;

}

}



/* SUMMARY */


async function generateSummary() {

    const summary =
        document.getElementById("summary");


    summary.textContent =
        "✦ Creating your AI summary...";


    try {

        const response =
            await fetch(
                `${API_URL}/summary`,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            summary.textContent =
                data.error ||
                "Summary generation failed.";

            return;

        }


        summary.textContent =
            data.summary;

    }
catch (error) {

    console.error("SUMMARY ERROR:", error);

    summary.textContent =
        "AI Error: " + error.message;

}

}



/* QUIZ */


async function generateQuiz() {

    const quiz =
        document.getElementById("quiz");


    const count =
        document.getElementById(
            "questionCount"
        ).value;


    const difficulty =
        document.getElementById(
            "difficulty"
        ).value;


    quiz.innerHTML =
        `<div class="result-box">
            ✦ Generating your personalized quiz...
        </div>`;


    try {

        const response =
            await fetch(
                `${API_URL}/quiz?number_of_questions=${count}&difficulty=${difficulty}`,
                {
                    method: "POST"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            quiz.innerHTML =
                `<div class="result-box">
                    ${data.error || "Quiz generation failed."}
                </div>`;

            return;

        }


        displayQuiz(
            data.quiz
        );

    }

    catch (error) {

    console.error("QUIZ ERROR:", error);

    quiz.innerHTML =
        `<div class="result-box">
            AI Error: ${error.message}
        </div>`;

}

}



/* DISPLAY QUIZ */


function displayQuiz(questions) {

    const container =
        document.getElementById("quiz");


    container.innerHTML = "";


    questions.forEach(
        (item, index) => {

            const question =
                document.createElement("div");


            question.className =
                "quiz-question";


            question.dataset.answer =
                item.correct_answer;


            let html =
                `<h3>
                    ${index + 1}. ${item.question}
                </h3>`;


            item.options.forEach(
                option => {

                    html += `
                        <label class="quiz-option">

                            <input
                                type="radio"
                                name="quiz-${index}"
                                value="${escapeHtml(option)}"
                            >

                            ${escapeHtml(option)}

                        </label>
                    `;

                }
            );


            question.innerHTML =
                html;


            container.appendChild(
                question
            );

        }
    );


    const submitButton =
        document.createElement("button");


    submitButton.className =
        "primary-button quiz-submit";


    submitButton.innerHTML =
        "Submit Quiz →";


    submitButton.onclick =
        calculateScore;


    container.appendChild(
        submitButton
    );

}



/* SCORE */


function calculateScore() {

    const questions =
        document.querySelectorAll(
            ".quiz-question"
        );


    let score = 0;


    questions.forEach(
        question => {

            const selected =
                question.querySelector(
                    "input:checked"
                );


            if (
                selected &&
                selected.value ===
                question.dataset.answer
            ) {

                score++;

            }

        }
    );


    const scoreDiv =
        document.createElement("div");


    scoreDiv.className =
        "score";


    scoreDiv.textContent =
        `🎯 Your Score: ${score} / ${questions.length}`;


    document.getElementById("quiz")
        .appendChild(scoreDiv);

}



/* BASIC HTML ESCAPE */


function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.textContent =
        text;

    return div.innerHTML;

}