// 模擬資料
const mockData = [
    { name: "感冒", departments: ["家醫科", "耳鼻喉科"], description: "常見的上呼吸道感染疾病，症狀包括咳嗽、鼻塞。" },
    { name: "流感", departments: ["家醫科", "內科"], description: "急性病毒感染，症狀包括發燒、咳嗽、肌肉痠痛。" },
    { name: "肺炎", departments: ["內科", "呼吸科"], description: "嚴重的肺部感染，症狀包括咳嗽、呼吸急促、發燒。" }
];

// 畫面切換
function switchPage(activePageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
        if (page.id === activePageId) {
            page.classList.add('active');
        }
    });
}

// 搜尋邏輯
function filterData(query) {
    const symptoms = query.split(" ").map(s => s.toLowerCase());
    return mockData
        .map(item => ({
            ...item,
            matchCount: symptoms.filter(symptom => item.description.toLowerCase().includes(symptom)).length
        }))
        .filter(item => item.matchCount > 0)
        .sort((a, b) => b.matchCount - a.matchCount);
}

// 渲染結果
function renderResults(data) {
    const container = document.getElementById("results-container");
    container.innerHTML = data.length
        ? data.map(item => `
            <div class="disease-card">
                <h3>${item.name}</h3>
                <p>症狀描述：${item.description}</p>
                <p class="department-info">推薦科室：${item.departments.join(", ")}</p>
                <a class="more-info" href="https://health.udn.com/health/search/${encodeURIComponent(item.name)}/disease?" target="_blank">查看更多資訊</a>
            </div>
        `).join("")
        : "<p>找不到相關結果，請嘗試其他搜尋。</p>";
}

// 主畫面搜尋邏輯
document.getElementById("search-btn").addEventListener("click", () => {
    const query = document.getElementById("search-input").value.trim();
    if (!query) {
        alert("請輸入症狀！");
        return;
    }
    switchPage("loading-page");
    setTimeout(() => {
        const results = filterData(query);
        renderResults(results);
        switchPage("results-page");
    }, 1000); // 模擬加載
});

// 返回主畫面
document.getElementById("back-btn").addEventListener("click", () => {
    switchPage("main-page");
});

// 結果畫面重新搜尋
document.getElementById("new-search-btn").addEventListener("click", () => {
    const query = document.getElementById("new-search-input").value.trim();
    if (!query) {
        alert("請輸入症狀！");
        return;
    }
    switchPage("loading-page");
    setTimeout(() => {
        const results = filterData(query);
        renderResults(results);
        switchPage("results-page");
    }, 1000);
});
