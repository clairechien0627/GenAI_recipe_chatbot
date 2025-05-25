// assets/js/custom.js
() => {
    // 1. 找到 Gradio 隱藏的輸入元件（single-line input 或 textarea）
    // 拿到包 textarea 的最外層 div
    const wrapper = document.getElementById('selected-textbox');
    if (!wrapper) {
        console.warn('沒找到 #selected-textbox wrapper，請確認 elem_id 是否正確');
        return;
    }
    // 在 wrapper 內真正的輸入欄
    const textarea = wrapper.querySelector('textarea');
    if (!textarea) {
        console.warn('wrapper 內沒找到 textarea');
        return;
    }

    // 2. 存放目前選取的索引
    const selected = new Set();

    // 3. 更新 textbox 與觸發 Gradio 輸入事件
    function updateTextbox() {
        textarea.value = Array.from(selected).join(',');
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
    }

    // 4. 事件委派：綁定在 document.body 上，對所有 .image-option 生效
    document.body.addEventListener('click', (e) => {
        const box = e.target.closest('.image-option');
        if (!box) return;

        const idx = box.getAttribute('data-index');
        if (!idx) return;

        // 切換選取狀態
        if (box.classList.contains('selected')) {
        box.classList.remove('selected');
        selected.delete(idx);
        } else {
        box.classList.add('selected');
        selected.add(idx);
        }

        updateTextbox();
    });

    // 5. 找到第一個 .image-option，取得其父容器，再用 MutationObserver 監聽新增／刪除節點
    const firstBox = document.querySelector('.image-option');
    if (firstBox) {
        const container = firstBox.parentNode;
        const mo = new MutationObserver((mutations) => {
        mutations.forEach((m) => {
            // 只要有新節點加入就自動觸發一次 updateTextbox（選取清單不動）
            if ([...m.addedNodes].some(n => n.nodeType === 1 && n.matches('.image-option'))) {
            // 新的 .image-option 會透過事件委派自動生效，這裡不需額外綁 listener
            // 如需清空舊選擇，可在此調用 selected.clear() 並 updateTextbox()
            }
        });
        });
        mo.observe(container, { childList: true });
    } else {
        console.warn('找不到任何 .image-option，無法啟用 MutationObserver');
    }

    // 6. 每次按下「搜尋」時，清空已選並更新 textbox
    const searchBtn = document.getElementById('search-btn');
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
        selected.clear();
        updateTextbox();
        });
    } else {
        console.warn('沒找到 #search-btn');
    }

    // 7. 每次按下「全選」時，全部選擇並更新 textbox
    const selectedAllBtn = document.getElementById('btn-all');
    if (selectedAllBtn) {
        selectedAllBtn.addEventListener('click', () => {
        document.querySelectorAll('.image-option').forEach(elem => {
            elem.classList.add('selected');
            selected.add(elem.getAttribute('data-index'));
        });
        updateTextbox();
        });
    } else {
        console.warn('沒找到 #search-btn');
    }

    // 8. 每次按下「取消全選」時，清空已選並更新 textbox
    const selectedNoneBtn = document.getElementById('btn-none');
    if (selectedNoneBtn) {
        selectedNoneBtn.addEventListener('click', () => {
        document.querySelectorAll('.image-option').forEach(elem => {
            elem.classList.remove('selected');
        });
        selected.clear();
        updateTextbox();
        });
    } else {
        console.warn('沒找到 #search-btn');
    }
}

