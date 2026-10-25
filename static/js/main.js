/* ==========================================================
   doanhnhan.wiki — Tương tác giao diện (không cần thư viện)
   ========================================================== */
(function () {
  'use strict';

  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  /* ---------- 1. Menu trên điện thoại (Mobile Drawer Navigation) ---------- */
  const initMobileNav = () => {
    $$('.menu-toggle').forEach((btn) => {
      const targetId = btn.getAttribute('aria-controls') || 'mobile-nav-drawer';
      const drawer = document.getElementById(targetId);
      if (!drawer) return;

      let savedScrollY = 0;

      const toggleMenu = (shouldOpen) => {
        const isOpen = typeof shouldOpen === 'boolean'
          ? shouldOpen
          : !drawer.classList.contains('is-open');

        if (isOpen) {
          savedScrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop || 0;
          document.body.style.position = 'fixed';
          document.body.style.top = `-${savedScrollY}px`;
          document.body.style.left = '0';
          document.body.style.right = '0';
          document.body.style.width = '100%';
          document.documentElement.classList.add('mobile-nav-open');
          document.body.classList.add('mobile-nav-open');

          drawer.classList.add('is-open');
          btn.setAttribute('aria-expanded', 'true');
          drawer.setAttribute('aria-hidden', 'false');

          const input = drawer.querySelector('input[type="search"]');
          if (input) setTimeout(() => input.focus(), 250);
        } else {
          drawer.classList.remove('is-open');
          btn.setAttribute('aria-expanded', 'false');
          drawer.setAttribute('aria-hidden', 'true');

          document.body.style.position = '';
          document.body.style.top = '';
          document.body.style.left = '';
          document.body.style.right = '';
          document.body.style.width = '';
          document.documentElement.classList.remove('mobile-nav-open');
          document.body.classList.remove('mobile-nav-open');

          window.scrollTo(0, savedScrollY);
        }
      };

      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMenu();
      });

      // Đóng khi bấm phím Escape
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
          toggleMenu(false);
        }
      });

      // Đóng khi nhấp vào liên kết điều hướng bên trong drawer
      drawer.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => {
          toggleMenu(false);
        });
      });

      // Tự động đóng nếu resize màn hình lớn hơn 960px
      window.addEventListener('resize', () => {
        if (window.innerWidth > 960 && drawer.classList.contains('is-open')) {
          toggleMenu(false);
        }
      }, { passive: true });
    });
  };
  initMobileNav();

  /* ---------- 1b. Tự động đóng thông báo nổi (Toast Notifications) ---------- */
  const initToasts = (root = document) => {
    root.querySelectorAll('.toast-item:not([data-initialized])').forEach((toast) => {
      toast.setAttribute('data-initialized', 'true');
      const delay = parseInt(toast.dataset.autoDismiss || '4500', 10);
      let timer = null;
      const dismiss = () => {
        toast.classList.add('is-hiding');
        setTimeout(() => toast.remove(), 260);
      };
      timer = setTimeout(dismiss, delay);
      toast.addEventListener('mouseenter', () => clearTimeout(timer));
      toast.addEventListener('mouseleave', () => { timer = setTimeout(dismiss, 2000); });
      toast.querySelector('.toast-close')?.addEventListener('click', dismiss);
    });
  };
  initToasts();

  window.showToast = (msg, type = 'success', timeout = 4000) => {
    let stack = document.querySelector('.toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'toast-stack';
      document.body.appendChild(stack);
    }
    const item = document.createElement('div');
    item.className = `toast-item toast-${type}`;
    item.dataset.autoDismiss = String(timeout);
    const icon = type === 'error' || type === 'danger' ? '✕' : (type === 'warning' ? '!' : '✓');
    item.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <div class="toast-content">${msg}</div>
      <button type="button" class="toast-close" aria-label="Đóng">&times;</button>
    `;
    stack.appendChild(item);
    initToasts(stack);
  };

  /* ---------- 1c. Phím tắt Tìm kiếm nhanh (⌘K / Ctrl+K / /) ---------- */
  document.addEventListener('keydown', (e) => {
    const active = document.activeElement;
    const isEditing = active && (active.tagName === 'INPUT' || active.tagName === 'TEXTAREA' || active.tagName === 'SELECT' || active.isContentEditable);
    if ((e.key.toLowerCase() === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !isEditing)) {
      e.preventDefault();
      const searchInput = document.querySelector('input[type="search"]') || document.querySelector('.search-bar input');
      if (searchInput) {
        searchInput.focus();
        if (typeof searchInput.select === 'function') searchInput.select();
      } else {
        window.location.href = '/tim-kiem/';
      }
    }
  });

  /* ---------- 1d. Nút Cuộn lên đầu trang (Back to Top) ---------- */
  const backToTopBtn = document.getElementById('btn-back-to-top');
  if (backToTopBtn) {
    let ticking = false;
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          if (window.scrollY > 350) {
            backToTopBtn.classList.add('is-visible');
          } else {
            backToTopBtn.classList.remove('is-visible');
          }
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });

    backToTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- 1e. Chống bấm đúp gửi trùng form (Anti-double submit) ---------- */
  $$('form[method="post"]:not([data-no-double-submit])').forEach((form) => {
    form.addEventListener('submit', (e) => {
      if (form.dataset.submitting === 'true') {
        e.preventDefault();
        return;
      }
      const submitBtn = form.querySelector('button[type="submit"]:not([disabled])');
      if (submitBtn) {
        form.dataset.submitting = 'true';
        setTimeout(() => {
          submitBtn.classList.add('is-loading');
        }, 10);
      }
    });
  });

  /* ---------- 2. Tab: lọc danh sách hoặc chuyển khung ----------
     <div data-tabs data-target="#grid">
       <button role="tab" data-filter="all|ten-nhom">…</button>     → lọc các [data-cat] trong #grid
       <button role="tab" aria-controls="panel-id">…</button>       → hiện khung tương ứng
     </div> */
  $$('[data-tabs]').forEach((group) => {
    const tabs = $$('[role="tab"]', group);
    const target = group.dataset.target ? $(group.dataset.target) : null;

    const activate = (tab) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', String(on));
        const panelId = t.getAttribute('aria-controls');
        if (panelId) {
          const panel = document.getElementById(panelId);
          if (panel) panel.hidden = !on;
        }
      });
      const filter = tab.dataset.filter;
      if (filter && target) {
        $$('[data-cat]', target).forEach((item) => {
          const cats = item.dataset.cat.split(/\s+/);
          item.hidden = !(filter === 'all' || cats.includes(filter));
        });
        const empty = target.parentElement && $('[data-empty]', target.parentElement);
        if (empty) empty.hidden = $$('[data-cat]', target).some((i) => !i.hidden);
      }
    };

    tabs.forEach((tab) => tab.addEventListener('click', () => activate(tab)));
    window.addEventListener('hashchange', () => {
      const t = tabs.find((x) => '#' + x.getAttribute('aria-controls') === location.hash);
      if (t) activate(t);
    });
    const fromHash = location.hash ? tabs.find((t) => '#' + t.getAttribute('aria-controls') === location.hash) : null;
    const start = fromHash || tabs.find((t) => t.getAttribute('aria-selected') === 'true') || tabs[0];
    if (start) activate(start);
  });

  /* ---------- 3. Sao chép (số tài khoản, nội dung chuyển khoản…) ---------- */
  const copyText = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (err) { ok = false; }
      document.body.removeChild(ta);
      return ok;
    }
  };
  $$('[data-copy]').forEach((btn) => {
    const label = btn.textContent;
    btn.addEventListener('click', async () => {
      const src = btn.dataset.copy.startsWith('#') ? $(btn.dataset.copy) : null;
      const text = src ? src.textContent.trim() : btn.dataset.copy;
      const ok = await copyText(text);
      btn.textContent = ok ? 'Đã sao chép' : 'Không sao chép được';
      setTimeout(() => { btn.textContent = label; }, 2000);
    });
  });

  /* ---------- 3b. Chia sẻ trang (Web Share API & Sao chép liên kết) ---------- */
  $$('[data-share-url]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const url = btn.dataset.shareUrl || window.location.href;
      const title = document.title || 'doanhnhan.wiki';
      if (navigator.share) {
        try {
          await navigator.share({ title, url });
          return;
        } catch (err) {
          if (err.name === 'AbortError') return;
        }
      }
      const ok = await copyText(url);
      if (ok) {
        if (window.showToast) {
          window.showToast('Đã sao chép liên kết vào bộ nhớ tạm!', 'success');
        } else {
          alert('Đã sao chép liên kết: ' + url);
        }
      }
    });
  });

  /* ---------- 4. Video: chỉ nhúng link, chỉ tải trình phát khi bấm ---------- */
  const toEmbed = (url) => {
    if (!url) return null;
    let u;
    try { u = new URL(url); } catch (e) { return null; }
    const host = u.hostname.replace(/^www\.|^m\./, '');
    let id = null;
    if (host === 'youtu.be') id = u.pathname.slice(1);
    if (host === 'youtube.com') {
      id = u.searchParams.get('v');
      const m = u.pathname.match(/^\/(shorts|live|embed)\/([^/?#]+)/);
      if (!id && m) id = m[2];
    }
    if (id) return { platform: 'YouTube', src: 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0' };
    if (host === 'vimeo.com') {
      const m = u.pathname.match(/\/(\d+)/);
      if (m) return { platform: 'Vimeo', src: 'https://player.vimeo.com/video/' + m[1] + '?autoplay=1' };
    }
    if (host === 'facebook.com' || host === 'fb.watch') {
      return { platform: 'Facebook', src: 'https://www.facebook.com/plugins/video.php?href=' + encodeURIComponent(url) + '&autoplay=true' };
    }
    if (host === 'tiktok.com') {
      const m = u.pathname.match(/\/video\/(\d+)/);
      if (m) return { platform: 'TikTok', src: 'https://www.tiktok.com/embed/v2/' + m[1] };
    }
    return { platform: host, src: null };
  };
  window.dnwVideoEmbed = toEmbed;

  const mountPlayer = (player) => {
    const btn = $('.player-btn', player);
    if (!btn) return;
    btn.addEventListener('click', () => {
      const url = player.dataset.videoUrl;
      const embed = toEmbed(url);
      if (!embed || !embed.src) { if (url) window.open(url, '_blank', 'noopener'); return; }
      const iframe = document.createElement('iframe');
      iframe.src = embed.src;
      iframe.title = player.dataset.videoTitle || 'Video';
      iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      iframe.allowFullscreen = true;
      iframe.loading = 'lazy';
      player.appendChild(iframe);
      btn.hidden = true;
    });
  };
  $$('.player').forEach(mountPlayer);

  // Thư viện video: bấm thẻ để đưa video lên trình phát nổi bật
  $$('[data-video-library]').forEach((lib) => {
    const player = $(lib.dataset.player);
    if (!player) return;
    const setText = (sel, text) => { $$(sel).forEach((el) => { el.textContent = text; }); };
    $$('[data-video]', lib).forEach((card) => {
      card.addEventListener('click', () => {
        $$('[data-video]', lib).forEach((c) => c.classList.toggle('is-selected', c === card));
        const d = card.dataset;
        player.dataset.videoUrl = d.url;
        player.dataset.videoTitle = d.title;
        const old = $('iframe', player); if (old) old.remove();
        const pb = $('.player-btn', player); if (pb) pb.style.backgroundImage = d.thumb ? "linear-gradient(rgba(11,26,46,.45),rgba(11,26,46,.45)),url('" + d.thumb.replace(/'/g, '%27') + "')" : '';
        const btn = $('.player-btn', player); if (btn) btn.hidden = false;
        setText('[data-now="title"]', d.title);
        setText('[data-now="kind"]', d.kind);
        setText('[data-now="who"]', d.who);
        setText('[data-now="platform"]', d.platform);
        setText('[data-now="duration"]', d.duration || '');
        const link = $('[data-now="link"]'); if (link) { link.href = d.url; link.textContent = 'Xem trên ' + d.platform + ' ↗'; }
        player.scrollIntoView({ behavior: 'smooth', block: 'center' });
      });
    });
  });

  /* ---------- 5. Ẩn khối khi không có dữ liệu (ví dụ khối Video) ---------- */
  $$('[data-hide-if-empty]').forEach((block) => {
    if (!$('[data-item]', block)) block.hidden = true;
  });

  /* ---------- 6. Đồng ý điều khoản: đủ ô bắt buộc mới bấm được ---------- */
  $$('[data-consent]').forEach((form) => {
    const required = $$('input[data-required]', form);
    const submit = $('[data-consent-submit]', form);
    const sync = () => {
      const ok = required.every((c) => c.checked);
      submit.disabled = !ok;
      submit.setAttribute('aria-disabled', String(!ok));
      submit.classList.toggle('btn-gold', ok);
    };
    required.forEach((c) => c.addEventListener('change', sync));
    sync();
    form.addEventListener('submit', (e) => {
      if (submit.disabled) e.preventDefault();
    });
  });

  /* ---------- 7. Gợi ý AI: chấp nhận / bỏ qua ---------- */
  const counter = $('[data-ai-count]');
  const updateCount = () => {
    if (counter) counter.textContent = $$('.ai-tip:not(.is-accepted):not(.is-dismissed)').length + ' chờ xử lý';
  };
  $$('.ai-tip').forEach((tip) => {
    const actions = $('.ai-actions', tip);
    const result = $('.ai-result', tip);
    $$('[data-ai]', tip).forEach((btn) => {
      btn.addEventListener('click', () => {
        const accept = btn.dataset.ai === 'accept';
        tip.classList.add(accept ? 'is-accepted' : 'is-dismissed');
        if (actions) actions.hidden = true;
        if (result) {
          result.hidden = false;
          result.textContent = accept
            ? (tip.dataset.okText || 'Đã chấp nhận · đã ghi nhật ký')
            : (tip.dataset.noText || 'Đã bỏ qua · đã ghi nhật ký');
        }
        updateCount();
      });
    });
  });
  updateCount();

  /* ---------- 8. Quản trị: chọn dòng trong hàng chờ ---------- */
  $$('[data-select-rows]').forEach((table) => {
    $$('tbody tr', table).forEach((tr) => {
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', () => {
        $$('tbody tr', table).forEach((r) => r.classList.toggle('is-active', r === tr));
        const title = $('[data-review-title]');
        if (title && tr.dataset.title) title.textContent = tr.dataset.title;
      });
    });
  });

  /* ---------- 9. Quản trị: xem trước link video ---------- */
  $$('[data-video-input]').forEach((input) => {
    const out = $(input.dataset.videoInput);
    const sync = () => {
      const e = toEmbed(input.value.trim());
      if (!out) return;
      if (!input.value.trim()) out.textContent = 'Dán link YouTube, Vimeo, Facebook hoặc TikTok';
      else if (!e) out.textContent = 'Link chưa hợp lệ';
      else if (!e.src) out.textContent = 'Nền tảng ' + e.platform + ': sẽ hiện dạng “Xem trên ' + e.platform + '”, không nhúng';
      else out.textContent = 'Nhận dạng: ' + e.platform + ' · sẽ lấy tiêu đề, ảnh bìa, thời lượng tự động';
    };
    input.addEventListener('input', sync);
    sync();
  });
  /* ---------- 10. Mật khẩu: nhập lại phải khớp, nút hiện/ẩn ---------- */
  $$('[data-password-confirm]').forEach((confirm) => {
    const form = confirm.form;
    const pw = form && $('[data-password]', form);
    if (!pw) return;
    const check = () => confirm.setCustomValidity(confirm.value && confirm.value !== pw.value ? 'Mật khẩu nhập lại chưa khớp' : '');
    pw.addEventListener('input', check);
    confirm.addEventListener('input', check);
  });
  $$('[data-toggle-password]').forEach((btn) => {
    const input = $(btn.dataset.togglePassword);
    if (!input) return;
    btn.addEventListener('click', () => {
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      btn.textContent = show ? 'Ẩn' : 'Hiện';
      btn.setAttribute('aria-pressed', String(show));
    });
  });

  /* ---------- 11. Trình soạn thảo đơn giản (markdown) ---------- */
  $$('.editor').forEach((ed) => {
    const ta = $('textarea', ed);
    if (!ta) return;
    $$('[data-md]', ed).forEach((btn) => {
      btn.addEventListener('click', () => {
        const [before, after = ''] = btn.dataset.md.split('|');
        const { selectionStart: a, selectionEnd: b, value: v } = ta;
        const sel = v.slice(a, b) || btn.dataset.placeholder || '';
        ta.value = v.slice(0, a) + before + sel + after + v.slice(b);
        ta.focus();
        ta.setSelectionRange(a + before.length, a + before.length + sel.length);
        ta.dispatchEvent(new Event('input'));
      });
    });
    const counter = $('[data-word-count]', ed);
    if (counter) {
      const count = () => { counter.textContent = (ta.value.trim().match(/\S+/g) || []).length + ' từ'; };
      ta.addEventListener('input', count);
      count();
    }
  });

  /* ---------- 12. Thêm dòng lặp (dấu mốc, nguồn, sản phẩm…) ---------- */
  $$('[data-repeat-add]').forEach((btn) => {
    const list = $(btn.dataset.repeatAdd);
    if (!list) return;
    btn.addEventListener('click', () => {
      const rows = $$('[data-repeat-row]', list);
      const last = rows[rows.length - 1];
      if (!last) return;
      const clone = last.cloneNode(true);
      $$('input, textarea', clone).forEach((el) => { el.value = ''; });
      $$('select', clone).forEach((el) => { el.selectedIndex = 0; });
      $$('[id]', clone).forEach((el) => { el.id = el.id.replace(/-\d+$/, '') + '-' + (rows.length + 1); });
      $$('label[for]', clone).forEach((el) => { el.htmlFor = el.htmlFor.replace(/-\d+$/, '') + '-' + (rows.length + 1); });
      list.appendChild(clone);
      const first = $('input, textarea', clone); if (first) first.focus();
    });
  });
  document.addEventListener('click', (e) => {
    const rm = e.target.closest('[data-repeat-remove]');
    if (!rm) return;
    const row = rm.closest('[data-repeat-row]');
    const list = row && row.parentElement;
    if (!row || !list) return;
    if ($$('[data-repeat-row]', list).length > 1) row.remove();
    else {
      $$('input, textarea', row).forEach((el) => { el.value = ''; });
      $$('select', row).forEach((el) => { el.selectedIndex = 0; });
    }
  });

  /* ---------- 13. Gợi ý tên khi nhập (doanh nghiệp, doanh nhân) ----------
     <input data-suggest="company|person" list="ds-company"> — điền <datalist> từ /api/goi-y/ */
  let suggestTimer = null;
  document.addEventListener('input', (e) => {
    const input = e.target.closest('[data-suggest]');
    if (!input) return;
    const list = document.getElementById(input.getAttribute('list'));
    const q = input.value.trim();
    clearTimeout(suggestTimer);
    if (!list || q.length < 2) return;
    suggestTimer = setTimeout(async () => {
      try {
        const res = await fetch('/api/goi-y/?loai=' + encodeURIComponent(input.dataset.suggest) + '&q=' + encodeURIComponent(q));
        if (!res.ok) return;
        const data = await res.json();
        list.innerHTML = '';
        data.results.forEach((r) => {
          const o = document.createElement('option');
          o.value = r.label;
          if (r.tax_code) o.dataset.tax = r.tax_code;
          if (r.name) o.dataset.name = r.name;
          list.appendChild(o);
        });
      } catch (err) { /* bỏ qua */ }
    }, 250);
  });

  /* Tự động đồng bộ và tra cứu giữa ô Doanh nghiệp và ô Mã số thuế */
  document.addEventListener('change', (e) => {
    const input = e.target.closest('[data-suggest="company"]');
    if (!input) return;
    const row = input.closest('[data-repeat-row]');
    if (!row) return;
    const taxInput = row.querySelector('[data-company-tax]');
    if (!taxInput) return;
    const val = input.value.trim();
    if (val.includes('(MST ') && val.endsWith(')')) {
      const match = val.match(/\(MST\s+([^)]+)\)$/);
      if (match) {
        if (!taxInput.value.trim()) {
          taxInput.value = match[1].trim();
        }
        input.value = val.replace(/\s*\(MST\s+[^)]+\)$/, '').trim();
      }
    }
  });

  let taxLookupTimer = null;
  document.addEventListener('input', (e) => {
    const taxInput = e.target.closest('[data-company-tax]');
    if (!taxInput) return;
    const row = taxInput.closest('[data-repeat-row]');
    if (!row) return;
    const nameInput = row.querySelector('[name="company_name"]');
    if (!nameInput) return;
    const tax = taxInput.value.trim();
    clearTimeout(taxLookupTimer);
    if (tax.length >= 10) {
      taxLookupTimer = setTimeout(async () => {
        try {
          const res = await fetch('/api/goi-y/?loai=company&q=' + encodeURIComponent(tax));
          if (!res.ok) return;
          const data = await res.json();
          const match = data.results && data.results.find((r) => r.tax_code === tax);
          if (match && match.name && !nameInput.value.trim()) {
            nameInput.value = match.name;
          }
        } catch (err) { /* bỏ qua */ }
      }, 300);
    }
  });


  /* ---------- 14. Hỏi lại trước thao tác quan trọng ---------- */
  document.addEventListener('submit', (e) => {
    const msg = e.target.dataset && e.target.dataset.confirm;
    if (msg && !window.confirm(msg)) e.preventDefault();
  }, true);

  /* ---------- 15. Hiện tên tệp đã chọn trong ô tải ảnh ---------- */
  $$('.upload-box input[type=file]').forEach((input) => {
    input.addEventListener('change', () => {
      const box = input.closest('.upload-box');
      let note = box && $('[data-file-name]', box);
      if (box && !note) { note = document.createElement('p'); note.className = 'hint'; note.dataset.fileName = ''; box.appendChild(note); }
      if (note) note.textContent = input.files.length ? 'Đã chọn: ' + input.files[0].name + ' — sẽ tải lên khi lưu' : '';
    });
  });

  /* ---------- 16. Gợi ý tìm kiếm tức thì (Live Autocomplete Search) ---------- */
  let searchTimer = null;
  let activeIndex = -1;

  const removeSearchDropdown = () => {
    $$('.search-autocomplete-dropdown').forEach((el) => el.remove());
    activeIndex = -1;
  };

  const setupSearchAutocomplete = (input) => {
    const form = input.closest('.search-bar');
    if (!form) return;
    form.style.position = 'relative';

    const renderResults = (results, query) => {
      removeSearchDropdown();
      if (!query || query.length < 2) return;

      const dropdown = document.createElement('div');
      dropdown.className = 'search-autocomplete-dropdown';
      dropdown.setAttribute('role', 'listbox');

      if (!results || results.length === 0) {
        dropdown.innerHTML = `<div class="search-autocomplete-empty">Không có gợi ý phù hợp cho “<strong>${escapeHtml(query)}</strong>”</div>`;
      } else {
        let html = '';
        results.forEach((item, idx) => {
          const imgHtml = item.image
            ? `<img src="${item.image}" alt="">`
            : `<span class="search-item-initials">${escapeHtml(item.initials || '')}</span>`;
          const badgeHtml = item.badge
            ? `<span class="search-item-badge">${escapeHtml(item.badge)}</span>`
            : '';
          html += `
            <a href="${item.url}" class="search-autocomplete-item" role="option" data-index="${idx}">
              <div class="search-item-media ${item.type === 'company' ? 'is-company' : ''}">${imgHtml}</div>
              <div class="search-item-body">
                <div class="search-item-title-row">
                  <span class="search-item-title">${escapeHtml(item.title)}</span>
                  <span class="search-item-type type-${item.type}">${escapeHtml(item.type_label)}</span>
                </div>
                <div class="search-item-sub">
                  <span class="search-item-desc">${escapeHtml(item.subtitle)}</span>
                  ${badgeHtml}
                </div>
              </div>
            </a>
          `;
        });
        html += `
          <a href="/tim-kiem/?q=${encodeURIComponent(query)}" class="search-autocomplete-footer">
            Xem tất cả kết quả cho “<strong>${escapeHtml(query)}</strong>” →
          </a>
        `;
        dropdown.innerHTML = html;
      }
      form.appendChild(dropdown);
    };

    const escapeHtml = (str) => {
      const p = document.createElement('p');
      p.textContent = str || '';
      return p.innerHTML;
    };

    input.addEventListener('input', () => {
      const q = input.value.trim();
      clearTimeout(searchTimer);
      if (q.length < 2) {
        removeSearchDropdown();
        return;
      }
      searchTimer = setTimeout(async () => {
        try {
          const res = await fetch('/api/goi-y/?q=' + encodeURIComponent(q));
          if (!res.ok) return;
          const data = await res.json();
          renderResults(data.results, q);
        } catch (err) {
          /* bỏ qua lỗi mạng */
        }
      }, 180);
    });

    input.addEventListener('keydown', (e) => {
      const dropdown = form.querySelector('.search-autocomplete-dropdown');
      if (!dropdown) return;
      const items = Array.from(dropdown.querySelectorAll('.search-autocomplete-item'));
      if (items.length === 0) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = (activeIndex + 1) % items.length;
        items.forEach((it, i) => it.classList.toggle('is-active', i === activeIndex));
        items[activeIndex].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = (activeIndex - 1 + items.length) % items.length;
        items.forEach((it, i) => it.classList.toggle('is-active', i === activeIndex));
        items[activeIndex].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' && activeIndex >= 0) {
        e.preventDefault();
        items[activeIndex].click();
      } else if (e.key === 'Escape') {
        removeSearchDropdown();
      }
    });
  };

  $$('.search-bar input[type="search"]').forEach(setupSearchAutocomplete);
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.search-bar')) {
      removeSearchDropdown();
    }
  });

  /* ---------- 17. Cửa sổ Chat Trợ lý AI (Conversational AI Assistant) ---------- */
  const initAiAssistant = () => {
    const launcher = document.getElementById('ai-launcher-btn');
    const drawer = document.getElementById('ai-assistant-drawer');
    const backdrop = document.getElementById('ai-assistant-backdrop');
    const closeBtn = document.getElementById('ai-drawer-close');
    const clearBtn = document.getElementById('ai-clear-chat');
    const messagesContainer = document.getElementById('ai-chat-messages');
    const chatInput = document.getElementById('ai-chat-input');
    const sendBtn = document.getElementById('ai-chat-send');
    const modelTag = document.getElementById('ai-model-tag');
    const contextTitle = document.getElementById('ai-context-title');

    // AI Settings Elements (Admin)
    const settingsToggle = document.getElementById('ai-settings-toggle');
    const settingsPanel = document.getElementById('ai-settings-panel');
    const settingsClose = document.getElementById('ai-settings-close');
    const apiKeyInput = document.getElementById('ai-setting-api-key');
    const keyStatus = document.getElementById('ai-setting-key-status');
    const modelSelect = document.getElementById('ai-setting-model');
    const saveSettingsBtn = document.getElementById('ai-settings-save-btn');
    const settingsFeedback = document.getElementById('ai-settings-feedback');

    if (!launcher || !drawer || !chatInput || !sendBtn) return;

    let conversationHistory = [];
    let pageContext = null;
    let lastActiveTextarea = null;

    // Tải cấu hình AI hiện tại
    const loadAiConfig = async () => {
      try {
        const res = await fetch('/quan-tri/api/cai-dat-ai/');
        if (!res.ok) return;
        const data = await res.json();
        if (data.ok && data.config) {
          const cfg = data.config;
          if (modelSelect && cfg.model) {
            modelSelect.value = cfg.model;
          }
          if (keyStatus) {
            if (cfg.has_key) {
              const srcText = cfg.source === 'database' ? 'Đã lưu trong Cài đặt Admin' : 'Đang dùng từ file .env';
              keyStatus.innerHTML = `✅ <b>Đã có API Key</b>: <code>${cfg.masked_key}</code> (${srcText})`;
              keyStatus.style.color = '#34d399';
            } else {
              keyStatus.innerHTML = `⚠️ <i>Chưa cài đặt API Key. Hãy dán mã để kích hoạt Gemini chính thức.</i>`;
              keyStatus.style.color = '#f59e0b';
            }
          }
          if (modelTag) {
            if (cfg.has_key) {
              modelTag.textContent = `Google Gemini (${cfg.model})`;
            } else {
              modelTag.textContent = `Editorial Engine (Nội bộ)`;
            }
          }
        }
      } catch (e) {
        // im lặng
      }
    };

    // Theo dõi textarea người dùng đang thao tác
    document.addEventListener('focusin', (e) => {
      if (e.target.tagName === 'TEXTAREA' && !e.target.closest('#ai-assistant-drawer')) {
        lastActiveTextarea = e.target;
      }
    });

    const openDrawer = () => {
      drawer.classList.add('is-open');
      if (backdrop) backdrop.classList.add('is-open');
      detectPageContext();
      loadAiConfig();
      setTimeout(() => chatInput.focus(), 200);
    };

    const closeDrawer = () => {
      drawer.classList.remove('is-open');
      if (backdrop) backdrop.classList.remove('is-open');
      if (settingsPanel) settingsPanel.style.display = 'none';
    };

    launcher.addEventListener('click', () => {
      if (drawer.classList.contains('is-open')) closeDrawer();
      else openDrawer();
    });

    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    if (backdrop) backdrop.addEventListener('click', closeDrawer);

    // Xử lý bật/tắt panel cài đặt AI
    if (settingsToggle && settingsPanel) {
      settingsToggle.addEventListener('click', () => {
        const isOpen = settingsPanel.style.display !== 'none';
        settingsPanel.style.display = isOpen ? 'none' : 'block';
        if (!isOpen) {
          loadAiConfig();
          if (apiKeyInput) apiKeyInput.focus();
        }
      });
    }

    if (settingsClose && settingsPanel) {
      settingsClose.addEventListener('click', () => {
        settingsPanel.style.display = 'none';
      });
    }

    if (saveSettingsBtn) {
      saveSettingsBtn.addEventListener('click', async () => {
        const newKey = apiKeyInput ? apiKeyInput.value.trim() : '';
        const newModel = modelSelect ? modelSelect.value : 'gemini-2.5-flash';

        saveSettingsBtn.disabled = true;
        if (settingsFeedback) {
          settingsFeedback.textContent = 'Đang lưu...';
          settingsFeedback.className = 'ai-settings-feedback';
        }

        try {
          const res = await fetch('/quan-tri/api/cai-dat-ai/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({
              gemini_api_key: newKey,
              gemini_model: newModel,
            }),
          });
          const data = await res.json();
          if (data.ok) {
            if (settingsFeedback) {
              settingsFeedback.textContent = '✓ ' + (data.message || 'Đã lưu!');
              settingsFeedback.className = 'ai-settings-feedback is-success';
            }
            if (apiKeyInput) apiKeyInput.value = '';
            await loadAiConfig();
            setTimeout(() => {
              if (settingsPanel) settingsPanel.style.display = 'none';
              if (settingsFeedback) settingsFeedback.textContent = '';
            }, 1800);
          } else {
            throw new Error(data.error || 'Không thể lưu cài đặt');
          }
        } catch (err) {
          if (settingsFeedback) {
            settingsFeedback.textContent = '❌ ' + (err.message || 'Lỗi lưu');
            settingsFeedback.className = 'ai-settings-feedback is-error';
          }
        } finally {
          saveSettingsBtn.disabled = false;
        }
      });
    }

    // Phím tắt Alt+A
    window.addEventListener('keydown', (e) => {
      if ((e.altKey && e.code === 'KeyA') || (e.altKey && e.key === 'a')) {
        e.preventDefault();
        if (drawer.classList.contains('is-open')) closeDrawer();
        else openDrawer();
      } else if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
        closeDrawer();
      }
    });

    // Tự động nhận diện ngữ cảnh trang
    const detectPageContext = () => {
      let name = '';
      let type = 'person';
      let typeLabel = 'Doanh nhân';

      const personInput = document.querySelector('input[name="full_name"]');
      const companyInput = document.querySelector('input[name="legal_name"]');

      if (personInput && personInput.value.trim()) {
        name = personInput.value.trim();
        type = 'person';
        typeLabel = 'Doanh nhân';
      } else if (companyInput && companyInput.value.trim()) {
        name = companyInput.value.trim();
        type = 'company';
        typeLabel = 'Doanh nghiệp';
      } else {
        const h1 = document.querySelector('h1');
        if (h1 && window.location.pathname.includes('/doanh-nhan/')) {
          name = h1.textContent.trim().split('(')[0].trim();
          type = 'person';
          typeLabel = 'Doanh nhân';
        } else if (h1 && window.location.pathname.includes('/doanh-nghiep/')) {
          name = h1.textContent.trim().split('(')[0].trim();
          type = 'company';
          typeLabel = 'Doanh nghiệp';
        }
      }

      if (name) {
        pageContext = { title: name, type, type_label: typeLabel, url: window.location.pathname };
        if (contextTitle) contextTitle.textContent = `${name} (${typeLabel})`;
      } else {
        pageContext = null;
        if (contextTitle) contextTitle.textContent = 'Soạn thảo tự do';
      }
    };

    // Auto-grow textarea
    chatInput.addEventListener('input', () => {
      chatInput.style.height = 'auto';
      chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // Enter to send
    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    sendBtn.addEventListener('click', (e) => {
      e.preventDefault();
      sendMessage();
    });

    // Gợi ý nhanh
    $$('.ai-quick-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const prompt = btn.dataset.prompt;
        if (!prompt) return;
        chatInput.value = prompt;
        chatInput.focus();
        chatInput.dispatchEvent(new Event('input'));
      });
    });

    // Nút làm mới chat
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        conversationHistory = [];
        messagesContainer.innerHTML = `
          <div class="ai-msg ai-msg-bot">
            <div class="ai-msg-bubble">
              <p>Cuộc trò chuyện đã được làm mới. Tôi sẵn sàng lắng nghe yêu cầu mới của bạn!</p>
            </div>
          </div>
        `;
      });
    }

    const appendUserMessage = (text) => {
      const msgDiv = document.createElement('div');
      msgDiv.className = 'ai-msg ai-msg-user';
      const bubble = document.createElement('div');
      bubble.className = 'ai-msg-bubble';
      bubble.textContent = text;
      msgDiv.appendChild(bubble);
      messagesContainer.appendChild(msgDiv);
      scrollToBottom();
    };

    const appendBotMessage = (text) => {
      const msgDiv = document.createElement('div');
      msgDiv.className = 'ai-msg ai-msg-bot';

      const bubble = document.createElement('div');
      bubble.className = 'ai-msg-bubble';
      bubble.innerHTML = renderMarkdown(text);
      msgDiv.appendChild(bubble);

      // Thêm nút thao tác nhanh
      const actions = document.createElement('div');
      actions.className = 'ai-bubble-actions';

      const copyBtn = document.createElement('button');
      copyBtn.className = 'ai-action-btn';
      copyBtn.type = 'button';
      copyBtn.textContent = '📋 Sao chép';
      copyBtn.addEventListener('click', async () => {
        await copyText(text);
        copyBtn.textContent = '✓ Đã sao chép';
        setTimeout(() => { copyBtn.textContent = '📋 Sao chép'; }, 2000);
      });
      actions.appendChild(copyBtn);

      const insertBtn = document.createElement('button');
      insertBtn.className = 'ai-action-btn btn-gold-mini';
      insertBtn.type = 'button';
      insertBtn.textContent = '📥 Chèn vào bài';
      insertBtn.addEventListener('click', async () => {
        let target = lastActiveTextarea;
        if (!target || !document.body.contains(target)) {
          target = document.querySelector('.editor textarea, form textarea');
        }
        if (target) {
          const prev = target.value;
          target.value = prev ? prev + '\n\n' + text : text;
          target.dispatchEvent(new Event('input', { bubbles: true }));
          target.scrollIntoView({ behavior: 'smooth', block: 'center' });
          insertBtn.textContent = '✓ Đã chèn';
          setTimeout(() => { insertBtn.textContent = '📥 Chèn vào bài'; }, 2000);
        } else {
          await copyText(text);
          insertBtn.textContent = '✓ Đã copy';
          setTimeout(() => { insertBtn.textContent = '📥 Chèn vào bài'; }, 2000);
        }
      });
      actions.appendChild(insertBtn);

      msgDiv.appendChild(actions);
      messagesContainer.appendChild(msgDiv);
      scrollToBottom();
    };

    const showTypingIndicator = () => {
      const id = 'ai-typing-indicator';
      const existing = document.getElementById(id);
      if (existing) existing.remove();

      const msgDiv = document.createElement('div');
      msgDiv.id = id;
      msgDiv.className = 'ai-msg ai-msg-bot';
      msgDiv.innerHTML = `
        <div class="ai-msg-bubble ai-typing-dots">
          <span class="ai-typing-dot"></span>
          <span class="ai-typing-dot"></span>
          <span class="ai-typing-dot"></span>
        </div>
      `;
      messagesContainer.appendChild(msgDiv);
      scrollToBottom();
    };

    const removeTypingIndicator = () => {
      const el = document.getElementById('ai-typing-indicator');
      if (el) el.remove();
    };

    const scrollToBottom = () => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    };

    const renderMarkdown = (str) => {
      if (!str) return '';
      // Escape HTML
      let html = str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      // Headers ###
      html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
      html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');

      // Bold **...**
      html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

      // Bullet lists
      html = html.replace(/^\s*-\s+(.*$)/gim, '<li>$1</li>');
      html = html.replace(/(<li>.*<\/li>)/gms, '<ul>$1</ul>');

      // Blockquotes
      html = html.replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>');

      // Paragraphs
      html = html.split(/\n{2,}/).map(para => {
        para = para.trim();
        if (!para) return '';
        if (para.startsWith('<h3>') || para.startsWith('<ul>') || para.startsWith('<blockquote>')) return para;
        return `<p>${para.replace(/\n/g, '<br>')}</p>`;
      }).join('');

      return html;
    };

    const getCsrfToken = () => {
      const match = document.cookie.match(/csrftoken=([^;]+)/);
      if (match) return match[1];
      const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
      return input ? input.value : '';
    };

    const sendMessage = async () => {
      const text = chatInput.value.trim();
      if (!text) return;

      appendUserMessage(text);
      conversationHistory.push({ role: 'user', content: text });

      chatInput.value = '';
      chatInput.style.height = 'auto';
      sendBtn.disabled = true;
      showTypingIndicator();

      try {
        const res = await fetch('/quan-tri/api/tro-ly-ai/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),
          },
          body: JSON.stringify({
            messages: conversationHistory,
            context: pageContext,
          }),
        });

        if (!res.ok) {
          throw new Error('Lỗi phản hồi máy chủ: ' + res.status);
        }

        const data = await res.json();
        removeTypingIndicator();

        const reply = data.reply || data.content || 'Đã tiếp nhận yêu cầu của bạn.';
        appendBotMessage(reply);
        conversationHistory.push({ role: 'model', content: reply });

        if (modelTag && data.model) {
          modelTag.textContent = data.model;
        }
      } catch (err) {
        removeTypingIndicator();
        appendBotMessage('⚠️ Có lỗi xảy ra khi liên lạc với AI: ' + (err.message || 'Lỗi kết nối'));
      } finally {
        sendBtn.disabled = false;
        chatInput.focus();
      }
    };
  };

  /* ---------- 27. Mở xem số điện thoại bảo mật (Chỉ Admin) ---------- */
  const initPhoneReveal = () => {
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.btn-reveal-phone');
      if (!btn) return;
      e.preventDefault();

      const pk = btn.dataset.pk;
      const url = btn.dataset.url;
      const target = document.getElementById(`phone-val-${pk}`);
      if (!target || !url) return;

      // Nếu đang hiển thị số thật, bấm lần nữa để ẩn lại
      if (btn.dataset.revealed === 'true') {
        target.textContent = btn.dataset.masked || '****';
        btn.dataset.revealed = 'false';
        btn.innerHTML = btn.tagName === 'BUTTON' && btn.classList.contains('btn') ? '👁️ Mở xem' : '[Mở xem]';
        return;
      }

      // Lưu lại giá trị masked hiện tại nếu chưa lưu
      if (!btn.dataset.masked) {
        btn.dataset.masked = target.textContent.trim();
      }

      const originalHtml = btn.innerHTML;
      btn.innerHTML = 'Đang tải…';
      btn.disabled = true;

      try {
        const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrf = csrfEl ? csrfEl.value : '';
        const res = await fetch(url, {
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf,
          },
        });
        if (!res.ok) {
          throw new Error('Chỉ Quản trị viên (Admin) mới có quyền mở xem số điện thoại.');
        }
        const data = await res.json();
        if (data.status === 'ok' && data.phone) {
          target.innerHTML = `<a href="tel:${data.phone.replace(/\s+/g, '')}" style="color:var(--gold-dark);font-weight:600;text-decoration:none">${data.phone}</a>`;
          btn.dataset.revealed = 'true';
          btn.innerHTML = btn.tagName === 'BUTTON' && btn.classList.contains('btn') ? '🔒 Ẩn số' : '[Ẩn số]';
          if (window.showToast) {
            window.showToast('Đã mở xem số điện thoại bảo mật (đã ghi log kiểm toán)', 'info', 2500);
          }
        } else {
          target.textContent = 'Chưa có SĐT';
          btn.innerHTML = originalHtml;
        }
      } catch (err) {
        if (window.showToast) {
          window.showToast(err.message || 'Không thể mở xem số điện thoại', 'danger');
        } else {
          alert(err.message);
        }
        btn.innerHTML = originalHtml;
      } finally {
        btn.disabled = false;
      }
    });
  };

  /* ---------- 16. Nút Thả tim / Like (Story, Podcast, Event, Person) ---------- */
  const initLikeButtons = () => {
    // 1. Đồng bộ trạng thái đã like từ localStorage khi tải trang
    document.querySelectorAll('[data-like-btn]').forEach((btn) => {
      const type = btn.dataset.type;
      const id = btn.dataset.id;
      if (type && id) {
        const isLiked = localStorage.getItem(`liked_${type}_${id}`) === 'true';
        if (isLiked) {
          btn.classList.add('is-liked');
        }
      }
    });

    // 2. Bắt sự kiện click (sử dụng delegation)
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('[data-like-btn]');
      if (!btn) return;

      e.preventDefault();
      e.stopPropagation();

      const type = btn.dataset.type;
      const id = btn.dataset.id;
      if (!type || !id) return;

      const countEl = btn.querySelector('[data-like-count]');
      let count = parseInt(btn.dataset.count || (countEl ? countEl.textContent.trim() : '0'), 10) || 0;
      const wasLiked = btn.classList.contains('is-liked');
      const willLike = !wasLiked;

      // Optimistic UI update
      if (willLike) {
        btn.classList.add('is-liked', 'animating');
        count += 1;
        localStorage.setItem(`liked_${type}_${id}`, 'true');
      } else {
        btn.classList.remove('is-liked');
        count = Math.max(0, count - 1);
        localStorage.removeItem(`liked_${type}_${id}`);
      }

      btn.dataset.count = String(count);
      if (countEl) countEl.textContent = count;

      setTimeout(() => btn.classList.remove('animating'), 400);

      // Đồng bộ tới tất cả các nút like khác cùng đối tượng trên trang
      document.querySelectorAll(`[data-like-btn][data-type="${type}"][data-id="${id}"]`).forEach(other => {
        if (other !== btn) {
          if (willLike) other.classList.add('is-liked');
          else other.classList.remove('is-liked');
          other.dataset.count = String(count);
          const oc = other.querySelector('[data-like-count]');
          if (oc) oc.textContent = count;
        }
      });

      // Gửi request API
      try {
        const getCookie = (name) => {
          let cookieValue = null;
          if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
              const c = cookies[i].trim();
              if (c.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(c.substring(name.length + 1));
                break;
              }
            }
          }
          return cookieValue;
        };
        const csrf = getCookie('csrftoken') || '';

        const res = await fetch('/api/toggle-like/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf,
          },
          body: JSON.stringify({
            type: type,
            id: id,
            action: willLike ? 'like' : 'unlike',
          }),
        });

        if (res.ok) {
          const data = await res.json();
          if (data.success && typeof data.likes_count === 'number') {
            document.querySelectorAll(`[data-like-btn][data-type="${type}"][data-id="${id}"]`).forEach(b => {
              b.dataset.count = String(data.likes_count);
              const c = b.querySelector('[data-like-count]');
              if (c) c.textContent = data.likes_count;
            });
          }
        }
      } catch (err) {
        console.warn('Lỗi cập nhật lượt thích:', err);
      }
    });
  };

  initAiAssistant();
  initPhoneReveal();
  initLikeButtons();
})();



