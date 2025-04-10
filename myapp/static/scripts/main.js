// 🔹 Auto-dismiss alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
      setTimeout(() => {
        alert.remove();
      }, 4000);
    });
  });
  
  // 🔹 Toggle password visibility
  function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
      input.type = input.type === 'password' ? 'text' : 'password';
    }
  }
  
  // 🔹 Show a loading spinner
  function showSpinner(spinnerId) {
    const spinner = document.getElementById(spinnerId);
    if (spinner) {
      spinner.style.display = 'inline-block';
    }
  }
  
  // 🔹 Simple form validation check
  function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
      form.classList.add('was-validated');
      return false;
    }
    return true;
  }
  