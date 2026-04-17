(function () {
  function copyUrl() {
    var el = document.getElementById('shareUrl');
    var btn = document.getElementById('copyShareUrlBtn');
    if (!el || !btn) {
      return;
    }

    navigator.clipboard.writeText(el.value)
      .then(function () {
        btn.innerText = 'Скопійовано';
        setTimeout(function () {
          btn.innerText = 'Копіювати';
        }, 1200);
      })
      .catch(function () {
        el.select();
        document.execCommand('copy');
      });
  }

  var copyBtn = document.getElementById('copyShareUrlBtn');
  if (copyBtn) {
    copyBtn.addEventListener('click', copyUrl);
  }
})();
