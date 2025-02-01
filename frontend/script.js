document.getElementById('convertButton').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const statusMessage = document.getElementById('status');
    const downloadSection = document.getElementById('download-section');
    const downloadLink = document.getElementById('downloadLink');

    if (fileInput.files.length === 0) {
        statusMessage.textContent = 'Please select at least one image file.';
        statusMessage.style.color = 'red';
        return;
    }

    // Create FormData to send the files
    const formData = new FormData();
    for (const file of fileInput.files) {
        formData.append('files', file);
    }

    // Show status message
    statusMessage.textContent = 'Processing images...';
    statusMessage.style.color = 'blue';

    try {
        const response = await fetch("/convert/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Error response:", errorText);  // Log the response from the backend
            throw new Error("Failed to convert images.");
        }

        const blob = await response.blob();
        const pdfUrl = URL.createObjectURL(blob);
        downloadLink.href = pdfUrl;
        downloadSection.style.display = "block";
        statusMessage.textContent = 'Conversion successful! You can download the PDF.';
        statusMessage.style.color = 'green';

    } catch (error) {
        console.error("Frontend Error:", error);  // Log the error on the frontend
        statusMessage.textContent = `Error: ${error.message}`;
        statusMessage.style.color = 'red';
    }
});
