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
  var input = document.querySelector(".char-input").value;
  
  // Create a blob with the input content
  var fileBlob = new Blob([input], { type: "text/plain" });

  // Create a FormData object and append the file to it
  var formData = new FormData();
  formData.append("file", fileBlob, "chara.txt");

  // Create an XMLHttpRequest object
  var xhr = new XMLHttpRequest();

  // Set up the request
  xhr.open("POST", "backend-url"); // Replace "backend-url" with the actual URL of your backend endpoint
  xhr.send(formData);
}
