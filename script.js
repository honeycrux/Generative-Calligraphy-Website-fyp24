const submitBtn = document.querySelector('.submitBtn');
submitBtn.addEventListener('click', handleSubmit);

function handleSubmit(event) {
  event.preventDefault();

  // Get user input
  const charInput = document.querySelector('.char-input');
  const userInput = charInput.value;

  // Read the content of the original text file
  // Localhost: http://192.168.56.1:8081
  fetch('http://192.168.56.1:8081/back-end/strokelist.txt', { mode: 'no-cors' })
    .then(response => response.text())
    .then(fileContent => {
      const rows = fileContent.split('\n');
      // Find the rows containing the input character
      // !! Cannot handle Chinese characters?
      const filteredRows = rows.filter(row => row.includes(userInput));

      if (filteredRows.length > 0) {
        // Generate the new file content by joining the filtered rows
        const newFileContent = filteredRows.join('\n');

        // Create a new Blob object with the file content
        const blob = new Blob([newFileContent], { type: 'text/plain;charset=utf-8' });

        // Create a temporary URL for the new Blob
        const filteredURL = URL.createObjectURL(blob);

        // Create a download link for the new text file
        const downloadLink = document.createElement('a');
        downloadLink.href = filteredURL;
        downloadLink.download = 'filtered_text.txt';

        // Trigger a click event to start the download
        downloadLink.dispatchEvent(new MouseEvent('click'));

        // Clean up the temporary URL
        URL.revokeObjectURL(filteredURL);

        console.log(`Character '${userInput}' found in the text file. Filtered rows saved in a new file.`);
      } else {
        console.log(`Character '${userInput}' not found in the text file.`);
      }
    })
    .catch(error => console.error('Error reading file:', error));
  }

function hasCharacter(row, character) {
  for (let i = 0; i < row.length; i++) {
    if (row.charAt(i) === character) {
      return true;
    }
  }
  return false;
}

function createTextFile() {

}
