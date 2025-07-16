const JobStatus = {
    Waiting: "waiting",
    Running: "running",
    Completed: "completed",
    Failed: "failed",
    Cancelled: "cancelled",
};

(function onLoad() {
    const submitBtn = document.querySelector(".submit-btn");
    submitBtn.addEventListener("click", handleSubmit);
})();

function constructUrl(endpoint = "") {
    if (!endpoint.startsWith("/")) {
        endpoint = "/" + endpoint;
    }

    const host = "127.0.0.1"; // Change this to your server's host if needed
    const port = 6701;
    const url = `http://${host}:${port}/fyp23${endpoint}`;

    return url;
}

function displayStatus(status) {
    document.getElementById("output-sample").style.display = "none";
    document.getElementById("output-result-container").style.display = "none";
    document.getElementById("output-loader").style.display = "block";

    // Update loader text to current status
    document.getElementById("status").innerText = status;
}

function enableSubmitButton() {
    const submitBtn = document.querySelector(".submit-btn");
    submitBtn.disabled = false;
}

async function handleSubmit(event) {
    event.preventDefault();

    const Modes = {
        Generation: "generation",
        Interruption: "interruption",
    };

    const submitBtn = document.querySelector(".submit-btn");
    const mode = submitBtn.classList.contains("submit-btn-generating") ? Modes.Interruption : Modes.Generation;

    switch (mode) {
        case Modes.Generation:
            await generateText();
            break;
        case Modes.Interruption:
            await interruptGeneration();
            break;
        default:
            console.error("Unknown mode:", mode);
            alert("An unknown error occurred. Please try again.");
    }
}

async function interruptGeneration() {
    const submitBtn = document.querySelector(".submit-btn");

    const jobId = submitBtn.getAttribute("data-job-id");
    if (!jobId) {
        console.error("No job ID found for interruption.");
        alert("No ongoing generation to interrupt.");
        return;
    }

    console.log(`[Interrupt Generation] Attempting to interrupt job with ID: ${jobId}`);

    const interruptUrl = constructUrl(`/interrupt_job`);
    const response = await fetch(interruptUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ job_id: jobId }),
    });

    if (!response.ok) {
        console.error("[Interrupt Generation] Failed to interrupt job");
        console.error(response);
        alert("Failed to interrupt the generation.");

        postGenerationFailureActions();
    }

    console.log("[Interrupt Generation] Job interrupted successfully");
}

function preGenerationActions() {
    const submitBtn = document.querySelector(".submit-btn");
    const downloadBtn = document.getElementById("download-btn");

    if (!submitBtn.classList.contains("submit-btn-generating")) {
        submitBtn.classList.add("submit-btn-generating");
    }

    if (downloadBtn.getAttribute("data-timer-interval")) {
        clearInterval(downloadBtn.getAttribute("data-timer-interval"));
        downloadBtn.removeAttribute("data-timer-interval");
    }
}

async function generateText() {
    displayStatus("Preparing for generation");

    preGenerationActions();

    // *************************** Getting and formatting input *****************************
    // Get user input
    const charInput = document.querySelector(".char-input");
    const inputText = charInput.value;
    // Matching user input into an array
    console.log("[Input Check] Obtained input text: ", inputText);

    // *************************** Input Check *****************************
    if (inputText.length < 1) {
        console.log("[Input Check] Empty character input!");
        alert("The input is empty. Please enter some characters for proper generation.");
        postGenerationFailureActions();
        return;
    }

    // *************************** Text Generation *****************************
    try {
        displayStatus("Generating");

        const job = await processGenerateRequest(inputText);

        if (job.job_status === JobStatus.Failed) {
            console.error(`[Text Generation] Job failed with error: ${job.job_info.error_message}`);
            alert(`Generation failed: ${job.job_info.error_message}`);
            postGenerationFailureActions();
            return;
        }

        if (job.job_status === JobStatus.Cancelled) {
            console.log("[Text Generation] Job was cancelled");
            postGenerationFailureActions();
            return;
        }

        if (job.job_status !== JobStatus.Completed) {
            console.error(`[Text Generation] Job completed with unexpected status`, job);
            alert("An unexpected error occurred during generation. Please try again.");
            postGenerationFailureActions();
            return;
        }

        console.log(`[Text Generation] Result generated`);

        postSuccessfulGenerationActions(job);

        console.log("[Text Generation] Process completed successfully");
    } catch (error) {
        console.error("Error occurred during text generation:", error);
        postGenerationFailureActions();
    }
}

async function processGenerateRequest(inputText) {
    console.log("[Generate Text] Initiating generation");

    const startJobUrl = constructUrl(`/start_job`);

    const startJobResponse = await fetch(startJobUrl, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            input_text: inputText,
        }),
    });

    if (!startJobResponse.ok) {
        console.error("[Generate Text] Failed to start job");
        console.error(startJobResponse);
        return;
    }

    const jobId = (await startJobResponse.json()).job_id;
    console.log(`[Generate Text] Job started with ID: ${jobId}`);

    const submitBtn = document.querySelector(".submit-btn");
    submitBtn.setAttribute("data-job-id", jobId);

    while (true) {
        const retrieveJobUrl = constructUrl(`/retrieve_job?job_id=${jobId}`);

        const retrieveJobResponse = await fetch(retrieveJobUrl);

        if (!retrieveJobResponse.ok) {
            console.error("[Generate Text] Failed to retrieve job status");
            console.error(retrieveJobResponse);
            return;
        }

        const job = await retrieveJobResponse.json();

        if (job.job_status === JobStatus.Completed || job.job_status === JobStatus.Failed || job.job_status === JobStatus.Cancelled) {
            return job;
        } else if (job.job_status === JobStatus.Waiting) {
            const positionInQueue = job.job_info.place_in_queue;
            displayStatus(`Waiting in queue at position ${positionInQueue}`);
        } else if (job.job_status === JobStatus.Running) {
            const runningStateMessage = job.job_info.running_state.message;
            displayStatus(runningStateMessage);
        } else {
            console.error("[Generate Text] Unknown job status:", job.job_status);
            return;
        }

        // Wait for 1 second before checking again
        await new Promise((resolve) => setTimeout(resolve, 1000));
    }
}

function postGenerationFailureActions() {
    document.getElementById("output-sample").style.display = "block";
    document.getElementById("output-result-container").style.display = "none";
    document.getElementById("output-loader").style.display = "none";

    const submitBtn = document.querySelector(".submit-btn");
    submitBtn.classList.remove("submit-btn-generating");
    submitBtn.removeAttribute("data-job-id");

    enableSubmitButton();
}

function postSuccessfulGenerationActions(job) {
    displayResults(job.job_result.generated_word_locations);
    enableSubmitButton();
    startButtonTimer();

    const submitBtn = document.querySelector(".submit-btn");
    submitBtn.classList.remove("submit-btn-generating");
    submitBtn.removeAttribute("data-job-id");
}

function displayResults(generatedWordLocations) {
    console.log("[Display Results] Displaying results");

    const picturesDiv = document.getElementById("pictures");
    picturesDiv.innerHTML = ""; // Clear previous images

    for (const wordLocation of generatedWordLocations) {
        const word = wordLocation.word;
        const success = wordLocation.success;
        const imageId = wordLocation.image_id;

        const img = document.createElement("img");

        if (success) {
            try {
                img.src = constructUrl(`/get_image?image_id=${imageId}`);
                img.classList.add("result-image"); // Add a CSS class to the image element
            } catch (error) {
                console.error(`[Display Results] Error setting image source for word ${word} with image id ${imageId}:`, error);
                img.src = "./static/blank-text.png"; // Fallback image
                img.classList.add("result-image"); // Add a CSS class to the image element
            }
        } else {
            img.src = "./static/blank-text.png"; // Fallback image
            img.classList.add("result-image"); // Add a CSS class to the image element
        }

        picturesDiv.appendChild(img);
    }

    document.getElementById("output-result-container").style.display = "flex";

    // Hide the loading element
    var loadingElement = document.getElementById("output-loader");
    loadingElement.style.display = "none";

    console.log("[Display Results] Results displayed");
}

function startButtonTimer() {
    const allowedDownloadTime = 59; // seconds
    const shouldDisplayTimer = (number) => number > 55 || number < 16;
    const downloadButton = document.getElementById("download-btn");

    // Enable download button
    undisplayButtonTimer();
    downloadButton.style.display = "block";

    // Set a timer for the download button
    let secondsLeft = allowedDownloadTime;
    const buttonTimerInterval = setInterval(() => {
        const timesUp = secondsLeft <= 0;
        if (timesUp) {
            clearInterval(buttonTimerInterval);
            undisplayButtonTimer();
            // Disable download
            downloadButton.style.display = "none";
            return;
        }
        const toDisplayTimer = shouldDisplayTimer(secondsLeft);
        if (toDisplayTimer) {
            displayButtonTimer(secondsLeft);
        } else {
            undisplayButtonTimer();
        }
        secondsLeft--;
    }, 1000);
    downloadButton.setAttribute("data-timer-interval", buttonTimerInterval);
}

function displayButtonTimer(secondsLeft) {
    const downloadButton = document.getElementById("download-btn");
    const timerClass = "download-btn-with-timer";
    if (!downloadButton?.classList.contains(timerClass)) {
        downloadButton.classList.add(timerClass);
    }
    downloadButton.innerText = secondsLeft.toString();
}

function undisplayButtonTimer() {
    const downloadButton = document.getElementById("download-btn");
    const timerClass = "download-btn-with-timer";
    if (downloadButton.classList.contains(timerClass)) {
        downloadButton.classList.remove(timerClass);
    }
    downloadButton.innerText = "";
}
