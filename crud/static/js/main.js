
const btnDelete= document.querySelectorAll('.btn-borrar');
if(btnDelete) {
  const btnArray = Array.from(btnDelete);
  btnArray.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      if(!confirm('¿Está seguro de querer borrar?')){
        e.preventDefault();
      }
    });
  })
}

function setTheme(theme) {
  localStorage.setItem('theme', theme);
  const themeLink = document.getElementById('theme-stylesheet');
  if (theme === 'oscuro') {
    themeLink.href = 'https://bootswatch.com/5/darkly/bootstrap.min.css';
  } else {
    themeLink.href = 'https://bootswatch.com/5/cosmo/bootstrap.min.css';
  }
}
