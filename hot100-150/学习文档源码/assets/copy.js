
(() => {
  function legacyCopy(text) {
    const active = document.activeElement;
    const selection = window.getSelection();
    const saved = [];
    if (selection) for (let i = 0; i < selection.rangeCount; i++) saved.push(selection.getRangeAt(i).cloneRange());
    const input = document.createElement('textarea');
    input.value = text;
    input.readOnly = true;
    input.setAttribute('aria-label', '待复制的代码');
    input.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0;font-size:16px;';
    document.body.append(input);
    try {
      input.focus({preventScroll:true});
      input.select();
      input.setSelectionRange(0, input.value.length);
      return document.execCommand('copy');
    } catch (_) { return false; }
    finally {
      input.remove();
      if (active && active.focus) active.focus({preventScroll:true});
      if (selection) { selection.removeAllRanges(); saved.forEach(range => selection.addRange(range)); }
    }
  }
  document.querySelectorAll('[data-copy-code]').forEach(button => {
    const code = document.getElementById('python-' + button.dataset.copyCode);
    const status = button.closest('.code-block').querySelector('.copy-status');
    let reset;
    button.hidden = false;
    button.addEventListener('click', async () => {
      clearTimeout(reset);
      status.textContent = '';
      status.classList.remove('copy-error');
      button.disabled = true;
      const source = code.textContent;
      let copied = false;
      try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(source);
          copied = true;
        }
      } catch (_) { /* file:// or an embedded browser may require the fallback. */ }
      if (!copied) copied = legacyCopy(source);
      button.disabled = false;
      if (copied) {
        button.textContent = '已复制';
        status.textContent = '已复制完整代码，保留原有缩进和换行。';
        reset = setTimeout(() => { button.textContent = '复制代码'; status.textContent = ''; }, 2500);
      } else {
        const selection = window.getSelection();
        if (selection) {
          const range = document.createRange(); range.selectNodeContents(code);
          selection.removeAllRanges(); selection.addRange(range);
        }
        button.textContent = '重试复制';
        status.classList.add('copy-error');
        const shortcut = /Mac|iPhone|iPad/.test(navigator.platform) ? '⌘C' : 'Ctrl+C';
        status.textContent = '浏览器未允许自动复制，已选中代码，请按 ' + shortcut + ' 复制。';
      }
    });
  });
})();
