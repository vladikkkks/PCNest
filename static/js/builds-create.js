(function () {
  function updateSummary() {
    var list = document.getElementById('selectedList');
    var totalEl = document.getElementById('selectedTotal');
    if (!list || !totalEl) return;

    var checked = document.querySelectorAll('input[name="components"]:checked');
    list.innerHTML = '';
    var total = 0;

    checked.forEach(function (input) {
      var name = input.dataset.name || 'Компонент';
      var price = parseFloat(input.dataset.price || '0');
      total += price;

      var li = document.createElement('li');
      var left = document.createElement('span');
      left.textContent = name;
      var right = document.createElement('strong');
      right.textContent = price.toFixed(0) + ' грн';
      li.appendChild(left);
      li.appendChild(right);
      list.appendChild(li);
    });

    totalEl.textContent = total.toFixed(0) + ' грн';
  }

  function setActiveButton(type) {
    var buttons = document.querySelectorAll('[data-filter]');
    buttons.forEach(function (btn) {
      btn.classList.toggle('active', btn.dataset.filter === type);
    });
  }

  function filterCards(type) {
    var cards = document.querySelectorAll('[data-component-type]');
    cards.forEach(function (card) {
      card.style.display = (type === 'all' || card.dataset.componentType === type) ? '' : 'none';
    });
    setActiveButton(type);
  }

  document.addEventListener('change', function (event) {
    if (event.target && event.target.name === 'components') {
      updateSummary();
    }
  });

  document.querySelectorAll('[data-filter]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterCards(btn.dataset.filter);
    });
  });

  // initial state
  updateSummary();
  filterCards('all');
})();
