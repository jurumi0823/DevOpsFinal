import pandas as pd

class Disease:
    def __init__(self, name, symptoms, complications,risk_groups, related_departments, affected_body_parts):
        self.name = name
        self.symptoms = symptoms
        self.complications = complications
        self.risk_groups = risk_groups
        self.related_departments = related_departments
        self.affected_body_parts = affected_body_parts

class SymptomAnalyzer:
    def __init__(self):
        self.selected_symptoms = []
        self.diseases = []

    def load_diseases(self, data_file):
        """載入疾病資料"""
        data = pd.read_csv(data_file)
        data.fillna("無", inplace=True)  # 將缺失值填充為 "無"
        self.diseases = [
            Disease(
                name=row["疾病名稱"],
                symptoms=row["症狀"].split(",") if row["症狀"] != "null" else ["無"],
                complications=row["併發症"].split(",") if row["併發症"] != "null" else ["無"],
                risk_groups=row["危險族群"].split(",") 
                            if "危險族群" in row and row["危險族群"] != "null" else "無",
                related_departments=[
                    dept.strip() for dept in row["科別"].replace("、", ",").split(",")
                ] if row["科別"] != "null" else ["無"],
                affected_body_parts=[
                    part.strip() for part in row["部位"].replace("、", ",").split(",")                    
                ]if row["部位"] != "null" else ["無"], 
            )
            for _, row in data.iterrows()
        ]

    def add_symptom(self, symptom):
        """新增症狀"""
        if symptom not in self.selected_symptoms:
            self.selected_symptoms.append(symptom)
        return {
            "status": "success",
            "selected_symptoms": self.selected_symptoms,
            "message": f"已新增症狀：'{symptom}'",
        }

    def reset_symptoms(self):
        """重置所有已選症狀"""
        self.selected_symptoms = []
        return {
            "status": "success",
            "selected_symptoms": [],
            "message": "所有症狀已重置",
        }

    def analyze_possible_diseases(self, symptom_match_threshold=0.6):
        matched_diseases = []
        department_count = {}

        # 篩選符合條件的疾病並計算症狀匹配比例
        for disease in self.diseases:
            # 計算交集，患者提及的症狀與疾病的症狀重疊
            matching_symptoms = set(self.selected_symptoms).intersection(disease.symptoms)
            match_ratio = len(matching_symptoms) / len(self.selected_symptoms)

            # 只有當覆蓋比例大於或等於 symptom_match_threshold，疾病才會加入匹配結果
            if match_ratio >= symptom_match_threshold:
                matched_diseases.append(
                    {
                        "name": disease.name,
                        "symptoms": disease.symptoms,
                        "complications": disease.complications,
                        "departments": disease.related_departments,
                        "risk_groups": disease.risk_groups,
                        "match_ratio": round(match_ratio, 2),  # 顯示匹配比例
                    }
                )
                # 統計推薦科室
                for department in disease.related_departments:
                    if department not in department_count:
                        department_count[department] = 0
                    department_count[department] += 1

        # 如果找不到相關疾病，返回提示
        if not matched_diseases:
            return {
                "status": "not_found",
                "selected_symptoms": self.selected_symptoms,
                "message": "根據您的輸入症狀，目前找不到符合條件的疾病，建議您檢查輸入內容或尋求專業醫療建議。",
                "recommended_departments": [],
                "matched_diseases": []
            }

        # 根據出現次數排名科室
        sorted_departments = sorted(department_count.items(), key=lambda x: x[1], reverse=True)

        # 返回結果
        return {
            "status": "success",
            "selected_symptoms": self.selected_symptoms,
            "recommended_departments": [{"department": dept, "count": count} for dept, count in sorted_departments],
            "matched_diseases": matched_diseases,
        }

# 測試
if __name__ == "__main__":
    analyzer = SymptomAnalyzer()
    analyzer.load_diseases("disease_data.csv") 
    
    # 模擬用戶輸入症狀
    print("新增症狀：")
    print(analyzer.add_symptom("胸悶"))
    print(analyzer.add_symptom("嘔吐")) 
    print(analyzer.add_symptom("食慾不振"))

    # 分析可能的疾病和推薦科室
    print("\n分析結果：")
    analysis_result = analyzer.analyze_possible_diseases()

    # 顯示推薦科室排名
    print("\n推薦科室排名：")
    for rank, department in enumerate(analysis_result["recommended_departments"], start=1):
        print(f"{rank}. {department['department']}（{department['count']} 次推薦）")

    # 顯示可能的疾病列表
    print("\n可能的疾病：")
    for disease in analysis_result["matched_diseases"]:
        print(f"- 疾病名稱：{disease['name']}")
        print(f"  症狀：{', '.join(disease['symptoms'])}")
        print(f"  併發症：{', '.join(disease['complications'])}")
        print(f"  推薦科室：{', '.join(disease['departments'])}")
        print(f"  危險族群：{disease['risk_groups']}")
        print("")
        