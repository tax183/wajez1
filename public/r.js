const API_BASE_URL = "http://localhost:3000"; // رابط الباك-إند

const pdfViewer = document.getElementById('pdfViewer');
const resultContainer = document.getElementById('resultText'); // ✅ المرجع الصحيح
const newFileBtn = document.getElementById('newFileBtn');
const fileInput = document.createElement('input');
fileInput.type = 'file';
fileInput.accept = 'application/pdf';

const uploadedFileName = sessionStorage.getItem('uploadedFileName');

if (uploadedFileName) {
  pdfViewer.src = `${API_BASE_URL}/uploads/${uploadedFileName}`;

  fetch(`${API_BASE_URL}/result/${uploadedFileName}`)
    .then(response => response.text()) // ✅ استقبل البيانات كـ HTML وليس JSON
    .then(data => {
      resultContainer.innerHTML = `<h2>Result</h2>${data}`;
    })
    .catch(error => {
      console.error('Error:', error);
      resultContainer.innerHTML = "<h2>Result</h2><p>Error loading data.</p>";
    });
}

newFileBtn.addEventListener('click', () => {
  fileInput.click();
});

fileInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    const formData = new FormData();
    formData.append('file', file);

    fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    })
      .then(response => response.json())
      .then(data => {
        sessionStorage.setItem('uploadedFileName', data.fileName);
        location.reload();
      })
      .catch(error => console.error('Upload Error:', error));
  }
});
