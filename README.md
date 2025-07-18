# lisova-poliana
Data Analysis for the Lisova Poliana center

Подготовка.
1. Экстракция данных:
- python main.py extract params
- вручную добавить параметрам в группах (много повторяющиеся) названия групп: "Амплітуда P (мкВ)" -> "Амплітуда P (мкВ) — відведення I"
- python main.py extract param-duplicates
- python main.py extract data --target-path=control_data.json --data-key=контроль
- python main.py extract data --target-path=treatment_data.json --data-key=Дих
- python main.py extract personal-data --source_path=raw_data.json --target-path=personal_data.json

2. Подготовка данных:
- python main.py data prep --source-path=control_data.json --meta-path=personal_data.json --target-path=control_data.json --treatment=0
- python main.py data prep --source-path=treatment_data.json --meta-path=personal_data.json --target-path=treatment_data.json --treatment=1
- python main.py data compute-deltas --source-path=control_data.json --target-path=control_delta.json
- python main.py data compute-deltas --source-path=treatment_data.json --target-path=treatment_delta.json
- python main.py data combine-deltas --delta1-path=control_delta.json --delta2-path=treatment_delta.json --target-path=combined_delta.json
- python main.py data delta-feature-inspect --source-path=combined_delta.json --noizy-feature-path=noizy_features.json --target-path=clean_delta.json
- python main.py data enrich-delta --source-path=clean_delta.json --meta-path=personal_data.json --target-path=delta.json

3. Эксперименты
- python main.py experiment baseline --source-paths control_data.json --source-paths treatment_data.json --target-folder=baseline


Все пациенты: мужчины и женщины
- сравниваем выборки до терапии: контрольная и дыхательная
- сравниваем контрольную группу: до терапии, после терапии
- сравниваем контрольную группу, 3х: до терапии, после терапии
- сравниваем контрольную группу, 5х: до терапии, после терапии
- сравниваем дыхательную группу: до терапии, после терапии
- сравниваем дельту: контрольная и дыхательная
- сравниваем дельту, 3хв: контрольная и дыхательная
- сравниваем дельту, 5хв: контрольная и дыхательная

Выбранные параметры:
- возможно какие-то выбранные параметры

Основные эксперименты:
- сравнение между группами до терапии
- сравнение внутри группы до терапии и после
- сравнение дельт (после терапии - до терапии) между группами

Характеристики выборки:
- все пациенты
- эксперимент: 3хв, 5хв
- пол: мужчины
- давление: норм, повышенное
- параметры: все, выбранные, каждый из выбранных
- пересечение всех параметров

Отдельный эксперимент:
- наиболее отзывчивые параметры