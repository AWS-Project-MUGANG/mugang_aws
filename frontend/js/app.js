// 모의 데이터
const mockSugangList = [
    { id: 1, college: "사회과학대학", department: "아동가족복지학과", subject: "인간행동과 사회환경", type: "전공필수", room: "대강당", credit: 3, capacity: 60, applied: 24 },
    { id: 2, college: "사회과학대학", department: "아동가족복지학과", subject: "여성과 사회", type: "교양필수", room: "온라인 강의", credit: 3, capacity: 200, applied: 198 },
    { id: 3, college: "사회과학대학", department: "아동가족복지학과", subject: "영어 회화 II", type: "교양선택", room: "306호", credit: 2, capacity: 15, applied: 15 },
    { id: 4, college: "사회과학대학", department: "아동가족복지학과", subject: "영유아 발달", type: "전공필수", room: "사 502호", credit: 3, capacity: 40, applied: 38 }
];
  
// 기존 장바구니 데이터 대신 백엔드에서 불러옵니다.
let cartData = [];

// 사용자 정보
const userId = localStorage.getItem('user_id');

// DOM 요소 
const cartTbody = document.getElementById('cart-tbody');
const sugangTbody = document.getElementById('sugang-tbody');
const panelSugang = document.getElementById('panel-sugang');
const panelTimetable = document.getElementById('panel-timetable');

// 탭 전환 기능
function switchTab(tabName) {
    // 모든 탭 버튼 비활성화
    document.querySelectorAll('.sidebar-nav .nav-item').forEach(btn => btn.classList.remove('active'));
    // 모든 패널 숨김
    document.querySelectorAll('.content-area .panel').forEach(panel => panel.style.display = 'none');
    
    // 선택된 탭 활성화
    if (tabName === 'sugang') {
        document.getElementById('tab-sugang').classList.add('active');
        panelSugang.style.display = 'block';
    } else if (tabName === 'timetable') {
        document.getElementById('tab-timetable').classList.add('active');
        panelTimetable.style.display = 'block';
    }
}

// 수강목록 렌더링
function renderSugangList() {
    sugangTbody.innerHTML = '';
    mockSugangList.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.college}</td>
            <td>${item.department}</td>
            <td>${item.subject}</td>
            <td>${item.type}</td>
            <td>${item.room}</td>
            <td>${item.credit}</td>
            <td>${item.capacity}</td>
            <td><button class="btn-apply" onclick="addToCart(${item.id})">담기</button></td>
        `;
        sugangTbody.appendChild(tr);
    });
}

// 장바구니 렌더링
function renderCart() {
    cartTbody.innerHTML = '';
    if (cartData.length === 0) {
        cartTbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#999;">신청된 수강 내역이 없습니다. (DB 비어있음)</td></tr>';
        return;
    }

    cartData.forEach(item => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.college}</td>
            <td>${item.department}</td>
            <td>${item.subject}</td>
            <td>${item.type}</td>
            <td>${item.room}</td>
            <td>2</td> <!-- 임시 학년 -->
            <td>${item.applied}</td>
            <td><button class="btn-apply" onclick="alert('수강신청 팝업 예정')">수강신청</button></td>
        `;
        cartTbody.appendChild(tr);
    });
}

// 수강신청(DB 저장) 로직 연동
window.addToCart = async function(id) {
    if (!userId) {
        alert("로그인 정보가 없습니다. 다시 로그인해주세요.");
        window.location.href = '../auth/login.html';
        return;
    }

    const item = mockSugangList.find(c => c.id === id);
    if (!item) return;

    const exists = cartData.find(c => c.subject === item.subject);
    if (exists) {
        alert("이미 수강신청(DB 저장)이 완료된 과목입니다.");
        return;
    }
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/enrollments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                subject: item.subject,
                college: item.college,
                department: item.department,
                room: item.room
            })
        });

        if (response.ok) {
            alert(`'${item.subject}' 수강신청이 데이터베이스에 정상 등록되었습니다.`);
            await loadEnrollments(); // DB에 저장되었으므로 다시 불러와서 화면에 반영합니다.
        } else {
            const errorData = await response.json();
            alert(`수강신청 실패: ${errorData.detail}`);
        }
    } catch (error) {
        console.error('Enroll error:', error);
        alert('서버 또는 DB 연결에 실패했습니다.');
    }
}

// DB에서 수강 내역 불러오기
async function loadEnrollments() {
    if (!userId) return;
    try {
        const response = await fetch(`http://localhost:8000/api/v1/enrollments/${userId}`);
        if (response.ok) {
            const data = await response.json();
            cartData = data.schedules;
            renderCart();
        }
    } catch (error) {
        console.error('Load enrollments error:', error);
    }
}

// 초기화
window.onload = async function() {
    // 세션 체크
    if(!localStorage.getItem('access_token')){
        window.location.href = '../auth/login.html';
        return;
    }
    renderSugangList();
    await loadEnrollments();
};
