import pandas as pd

# Constructing the evaluation dataset
data = {
    "Questions": [
        "패타는 어떤 특징이 있는 메신저인가요?",
        "인증 문자가 오지 않는데 어떻게 하나요?",
        "탈퇴하고 싶어요.",
        "해외 번호로도 가입이 되나요?",
        "패타 계정이 무엇인가요?",
        "프로필 이미지는 몇 개까지 등록 가능한가요?",
        "친구는 어떻게 추가하나요?"
    ],
    "Réponses": [
        "패타는 1:1 비밀 대화, 대화 자동 삭제 기능으로 프라이버시를 보장하며, 프라이빗 친구 연결, MY 일정·캘린더·디데이·알람 관리 기능, 다양한 무료 이모티콘 및 버블티콘을 제공합니다.",
        "네트워크 연결 상태에 따라 인증 문자 수신이 지연될 수 있으니, 잠시 후 다시 확인해 주세요.",
        "설정 > 계정 > 탈퇴하기 경로를 통해 계정을 탈퇴할 수 있으며, 탈퇴 시 모든 서비스 이용이 불가하고 이전 데이터를 복원할 수 없습니다.",
        "현재는 대한민국(+82) 번호로만 가입이 가능하며, 해외 번호는 추후 지원될 예정입니다.",
        "패타 계정은 전화번호 또는 이메일을 기반으로 생성되며, 기기나 번호 변경 시 동일 계정으로 로그인하면 이전 정보를 유지할 수 있습니다.",
        "프로필 이미지는 개수 제한 없이 등록할 수 있습니다.",
        "메인 화면 우측 상단의 친구 추가 버튼을 눌러 초대 가능한 친구 목록을 확인한 후 SMS 또는 앱 공유로 초대하면 상대방의 수락을 통해 친구가 등록됩니다."
    ],
    "Prédiction": [""] * 7,
    "Levenshtein_Distance": [""] * 7,
    "Cosine_Distance": [""] * 7
}

df = pd.DataFrame(data)

# Save to TSV
file_path = "./data/gitbook_evaluation_dataset.tsv"
df.to_csv(file_path, sep='\t', index=False)

# # Display to user
# import ace_tools as tools; tools.display_dataframe_to_user(name="evaluation_dataset.tsv preview", dataframe=df)

# file_path
