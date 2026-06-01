

// Function to set the theme based on localStorage or default to light mode
function applyTheme() {
    const body = document.body;
    const savedTheme = localStorage.getItem('theme') || 'is-paper'; // Default to 'is-paper' (light theme)
    const isDarkMode = savedTheme === 'is-dark';
  
    body.classList.remove('is-paper', 'is-dark');
    body.classList.add(savedTheme);
  
    // Toggle icons based on theme
    const lightIcon = document.querySelector('.light-icon');
    const darkIcon = document.querySelector('.dark-icon');
    if (isDarkMode) {
      lightIcon.style.display = 'none';
      darkIcon.style.display = 'block';
    } else {
      lightIcon.style.display = 'block';
      darkIcon.style.display = 'none';
    }
  
    // Update images to match the current theme
    document.querySelectorAll('img[data-icon-light][data-icon-dark]').forEach(icon => {
      const newSrc = isDarkMode ? icon.getAttribute('data-icon-dark') : icon.getAttribute('data-icon-light');
      icon.src = newSrc;
      icon.srcset = `${newSrc} 2x`; // For high-resolution images
    });

    // Match the Grafana panels to the current theme (rewrite their ?theme= param)
    const grafanaTheme = isDarkMode ? 'dark' : 'light';
    document.querySelectorAll('iframe.grafana-iframe').forEach(frame => {
      const newSrc = frame.src.replace(/([?&]theme=)(light|dark)/, `$1${grafanaTheme}`);
      if (newSrc !== frame.src) frame.src = newSrc; // only reload if it actually changed
    });
  }
  
  // Event listener for the theme toggle button
  document.getElementById('theme-toggle').addEventListener('click', function () {
    const body = document.body;
  
    // Toggle theme class on body
    if (body.classList.contains('is-paper')) {
      body.classList.replace('is-paper', 'is-dark');
      localStorage.setItem('theme', 'is-dark'); // Save theme to localStorage
    } else {
      body.classList.replace('is-dark', 'is-paper');
      localStorage.setItem('theme', 'is-paper'); // Save theme to localStorage
    }
  
    // Update icons and images after theme change
    applyTheme();
  });
  
  // Apply the saved theme on page load
  document.addEventListener('DOMContentLoaded', applyTheme);
  



  
  
  /*
  document.getElementById('theme-toggle').addEventListener('click', function () {
    const body = document.body;
    const lightIcon = this.querySelector('.light-icon');
    const darkIcon = this.querySelector('.dark-icon');

    // Toggle theme class on body
    if (body.classList.contains('is-paper')) {
      body.classList.replace('is-paper', 'is-dark');
      lightIcon.style.display = 'none';
      darkIcon.style.display = 'block';
    } else {
      body.classList.replace('is-dark', 'is-paper');
      lightIcon.style.display = 'block';
      darkIcon.style.display = 'none';
    }

    // Swap icon sources based on the theme
    const isDarkMode = body.classList.contains('is-dark');
    document.querySelectorAll('img[data-icon-light][data-icon-dark]').forEach(icon => {
      const newSrc = isDarkMode ? icon.getAttribute('data-icon-dark') : icon.getAttribute('data-icon-light');
      icon.src = newSrc;
      icon.srcset = `${newSrc} 2x;`  // Update srcset if used for high-resolution images
    });
  });

*/