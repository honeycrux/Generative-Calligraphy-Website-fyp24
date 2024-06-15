const submitBtn = document.querySelector('.submitBtn');
submitBtn.addEventListener('click', handleSubmit);

function handleSubmit(event) {
  event.preventDefault();

  // Get user input
  const charInput = document.querySelector('.char-input');
  const userInput = charInput.value;

  // Display result
  const outputContainer = document.querySelector('.output-container');
  const outputImg = document.querySelector('#output-img');
  outputImg.setAttribute('src', ' ');

  const stampImg = document.querySelector('#stamp');
  stampImg.setAttribute('src', './front-end/wanxizhi_stamp.png');
}

const submitBtn = document.querySelector('.submitBtn');
submitBtn.addEventListener('click', handleSubmit);

function handleSubmit(event) {
  event.preventDefault();

  // Get user input
  const charInput = document.querySelector('.char-input');
  const userInput = charInput.value;

  // Display result
  const outputContainer = document.querySelector('.output-container');
  const outputImg = document.querySelector('#output-img');
  outputImg.setAttribute('src', ' ');

  const stampImg = document.querySelector('#stamp');
  stampImg.setAttribute('src', './front-end/wanxizhi_stamp.png');
}

// Transform raw input into a txt. file
function createTextFile() {
  var input = document.querySelector(".char-input").value; // Get the input from the char-input field
  var fileBlob = new Blob([input], { type: "text/plain" });

  // Create a temporary link element
  var link = document.createElement("a");
  link.href = URL.createObjectURL(fileBlob);
  link.download = "output.txt";

  // Append the link to the document and click it to triggerthe file download
  document.body.appendChild(link);
  link.click();

  // Clean up the temporary link
  document.body.removeChild(link);
}
