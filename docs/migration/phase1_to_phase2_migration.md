---
category: migration
ai_context: medium
last_updated: 2025-10-18
related_docs:
  - ../bulk-data-fetch.md
---

# Phase 1 縺九ｉ Phase 2 縺ｸ縺ｮ遘ｻ陦後ぎ繧､繝・

## 讎りｦ・

縺薙・繝峨く繝･繝｡繝ｳ繝医・縲∝・驫俶氛荳諡ｬ蜿門ｾ励す繧ｹ繝・Β縺ｮPhase 1・・VP螳溯｣・ｼ峨°繧臼hase 2・磯ｫ伜ｺｦ縺ｪ繝舌ャ繝∝・逅・お繝ｳ繧ｸ繝ｳ・峨∈縺ｮ遘ｻ陦後↓縺､縺・※隱ｬ譏弱＠縺ｾ縺吶・

## 螳溯｣・・螳ｹ

### Phase 1 (譌｢蟄・
- **繧ｸ繝ｧ繝也ｮ｡逅・*: 繧､繝ｳ繝｡繝｢繝ｪ邂｡逅・ｼ・OBS霎樊嶌・・
- **豌ｸ邯壽ｧ**: 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜀崎ｵｷ蜍墓凾縺ｫ繧ｸ繝ｧ繝匁ュ蝣ｱ縺悟､ｱ繧上ｌ繧・
- **API**: `/api/bulk/start`, `/api/bulk/status/<job_id>`, `/api/bulk/stop/<job_id>`
- **隴伜挨蟄・*: job_id (萓・ "job-1720000000000")

### Phase 2 (譁ｰ隕・
- **繧ｸ繝ｧ繝也ｮ｡逅・*: 繝・・繧ｿ繝吶・繧ｹ豌ｸ邯壼喧・・atch_executions 繝・・繝悶Ν・・
- **豌ｸ邯壽ｧ**: 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜀崎ｵｷ蜍募ｾ後ｂ繝舌ャ繝∵ュ蝣ｱ縺御ｿ晄戟縺輔ｌ繧・
- **API**: 譌｢蟄連PI縺ｨ莠呈鋤諤ｧ繧剃ｿ昴■縺ｪ縺後ｉ縲｜atch_db_id繧りｿ泌唆
- **隴伜挨蟄・*: batch_db_id (萓・ 1, 2, 3...)

## 荳ｻ隕√↑螟画峩轤ｹ

### 1. 繝・・繧ｿ繝吶・繧ｹ繝・・繝悶Ν縺ｮ霑ｽ蜉

**batch_executions 繝・・繝悶Ν**
```sql
CREATE TABLE batch_executions (
    id SERIAL PRIMARY KEY,
    batch_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_stocks INTEGER NOT NULL,
    processed_stocks INTEGER DEFAULT 0,
    successful_stocks INTEGER DEFAULT 0,
    failed_stocks INTEGER DEFAULT 0,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**batch_execution_details 繝・・繝悶Ν**
```sql
CREATE TABLE batch_execution_details (
    id SERIAL PRIMARY KEY,
    batch_execution_id INTEGER NOT NULL,
    stock_code VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    records_inserted INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 譁ｰ隕上し繝ｼ繝薙せ繧ｯ繝ｩ繧ｹ

**BatchService 繧ｯ繝ｩ繧ｹ** (`app/services/batch_service.py`)
- 繝舌ャ繝∝ｮ溯｡梧ュ蝣ｱ縺ｮCRUD謫堺ｽ懊ｒ謠蝉ｾ・
- 繝・・繧ｿ繝吶・繧ｹ縺ｨ縺ｮ繧・ｊ蜿悶ｊ繧呈歓雎｡蛹・

荳ｻ隕√Γ繧ｽ繝・ラ:
- `create_batch()`: 譁ｰ隕上ヰ繝・メ菴懈・
- `get_batch()`: 繝舌ャ繝∵ュ蝣ｱ蜿門ｾ・
- `update_batch_progress()`: 騾ｲ謐玲峩譁ｰ
- `complete_batch()`: 繝舌ャ繝∝ｮ御ｺ・
- `create_batch_detail()`: 繝舌ャ繝∬ｩｳ邏ｰ菴懈・
- `update_batch_detail()`: 繝舌ャ繝∬ｩｳ邏ｰ譖ｴ譁ｰ

### 3. API繧ｨ繝ｳ繝峨・繧､繝ｳ繝医・諡｡蠑ｵ

**POST `/api/bulk/start`**

Phase 1縺ｮ繝ｬ繧ｹ繝昴Φ繧ｹ:
```json
{
  "success": true,
  "job_id": "job-1720000000000",
  "status": "accepted"
}
```

Phase 2縺ｮ繝ｬ繧ｹ繝昴Φ繧ｹ・井ｸ倶ｽ堺ｺ呈鋤諤ｧ繧剃ｿ晄戟・・
```json
{
  "success": true,
  "job_id": "job-1720000000000",
  "batch_db_id": 1,
  "status": "accepted"
}
```

**GET `/api/bulk/status/<job_id>`**

Phase 1縺ｨPhase 2縺ｮ荳｡譁ｹ縺ｫ蟇ｾ蠢・
- `job_id`縺・"job-" 縺ｧ蟋九∪繧句ｴ蜷・ Phase 1縺ｮ繧､繝ｳ繝｡繝｢繝ｪ邂｡逅・°繧牙叙蠕・
- `job_id`縺梧焚蛟､縺ｮ蝣ｴ蜷・ Phase 2縺ｮ繝・・繧ｿ繝吶・繧ｹ縺九ｉ蜿門ｾ・

## 遘ｻ陦梧焔鬆・

### 繧ｹ繝・ャ繝・: 繝・・繧ｿ繝吶・繧ｹ繝槭う繧ｰ繝ｬ繝ｼ繧ｷ繝ｧ繝ｳ螳溯｡・

```bash
python app/migrations/create_batch_execution_tables.py upgrade
```

### 繧ｹ繝・ャ繝・: 迺ｰ蠅・､画焚險ｭ螳夲ｼ医が繝励す繝ｧ繝ｳ・・

Phase 2讖溯・繧堤┌蜉ｹ蛹悶＠縺溘＞蝣ｴ蜷・
```bash
# .env 繝輔ぃ繧､繝ｫ縺ｫ霑ｽ蜉
ENABLE_PHASE2=false
```

繝・ヵ繧ｩ繝ｫ繝医〒縺ｯ譛牙柑縺ｧ縺呻ｼ・ENABLE_PHASE2=true`・峨・

### 繧ｹ繝・ャ繝・: 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜀崎ｵｷ蜍・

```bash
# 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ繧貞・襍ｷ蜍・
python app/app.py
```

## 蜍穂ｽ懃｢ｺ隱・

### Phase 1莠呈鋤諤ｧ繝・せ繝・

譌｢蟄倥・繧ｯ繝ｩ繧､繧｢繝ｳ繝医さ繝ｼ繝峨′蠑輔″邯壹″蜍穂ｽ懊☆繧九％縺ｨ繧堤｢ｺ隱・

```bash
# 繧ｸ繝ｧ繝夜幕蟋・
curl -X POST http://localhost:8000/api/bulk/start \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: your-api-key" \
  -d '{"symbols": ["7203.T", "6758.T"], "interval": "1d"}'

# 繝ｬ繧ｹ繝昴Φ繧ｹ萓・
# {
#   "success": true,
#   "job_id": "job-1720000000000",
#   "batch_db_id": 1,  # Phase 2縺ｧ縺ｯ霑ｽ蜉
#   "status": "accepted"
# }

# 繧ｸ繝ｧ繝悶せ繝・・繧ｿ繧ｹ遒ｺ隱搾ｼ・hase 1蠖｢蠑擾ｼ・
curl http://localhost:8000/api/bulk/status/job-1720000000000 \
  -H "X-API-KEY: your-api-key"

# 繧ｸ繝ｧ繝悶せ繝・・繧ｿ繧ｹ遒ｺ隱搾ｼ・hase 2蠖｢蠑擾ｼ・
curl http://localhost:8000/api/bulk/status/1 \
  -H "X-API-KEY: your-api-key"
```

### Phase 2繝・・繧ｿ繝吶・繧ｹ遒ｺ隱・

PostgreSQL縺ｧ繝舌ャ繝∝ｮ溯｡梧ュ蝣ｱ繧堤｢ｺ隱・

```sql
-- 繝舌ャ繝∝ｮ溯｡梧ュ蝣ｱ荳隕ｧ
SELECT * FROM batch_executions ORDER BY start_time DESC LIMIT 10;

-- 繝舌ャ繝∝ｮ溯｡瑚ｩｳ邏ｰ・育音螳壹・繝舌ャ繝・ｼ・
SELECT * FROM batch_execution_details WHERE batch_execution_id = 1;
```

## 荳倶ｽ堺ｺ呈鋤諤ｧ

Phase 2螳溯｣・〒縺ｯ縲∵里蟄倥・Phase 1繧ｯ繝ｩ繧､繧｢繝ｳ繝医さ繝ｼ繝峨→縺ｮ螳悟・縺ｪ荳倶ｽ堺ｺ呈鋤諤ｧ繧剃ｿ晄戟縺励※縺・∪縺・

1. **Phase 1縺ｮjob_id縺ｯ蠑輔″邯壹″菴ｿ逕ｨ蜿ｯ閭ｽ**: "job-XXXX" 蠖｢蠑上・ID縺ｧ繧ｹ繝・・繧ｿ繧ｹ蜿門ｾ怜庄閭ｽ
2. **Phase 1縺ｮ繝ｬ繧ｹ繝昴Φ繧ｹ蠖｢蠑上ｒ邯ｭ謖・*: 譌｢蟄倥・繧ｯ繝ｩ繧､繧｢繝ｳ繝医・螟画峩荳崎ｦ・
3. **Phase 2縺ｮ霑ｽ蜉諠・ｱ縺ｯ繧ｪ繝励す繝ｧ繝ｳ**: batch_db_id縺ｯ霑ｽ蜉諠・ｱ縺ｨ縺励※霑泌唆縺輔ｌ繧九′縲∫┌隕悶＠縺ｦ繧ょ虚菴懊↓蠖ｱ髻ｿ縺ｪ縺・

## 繝医Λ繝悶Ν繧ｷ繝･繝ｼ繝・ぅ繝ｳ繧ｰ

### Phase 2讖溯・縺悟虚菴懊＠縺ｪ縺・

**蜴溷屏**: 繝・・繧ｿ繝吶・繧ｹ繝・・繝悶Ν縺御ｽ懈・縺輔ｌ縺ｦ縺・↑縺・

**蟇ｾ蜃ｦ**:
```bash
python app/migrations/create_batch_execution_tables.py upgrade
```

### 繝舌ャ繝∵ュ蝣ｱ縺後ョ繝ｼ繧ｿ繝吶・繧ｹ縺ｫ菫晏ｭ倥＆繧後↑縺・

**蜴溷屏**: `ENABLE_PHASE2`迺ｰ蠅・､画焚縺掲alse縺ｫ險ｭ螳壹＆繧後※縺・ｋ

**蟇ｾ蜃ｦ**:
```bash
# .env繝輔ぃ繧､繝ｫ繧堤｢ｺ隱・
cat .env | grep ENABLE_PHASE2

# 蠢・ｦ√↓蠢懊§縺ｦ菫ｮ豁｣
echo "ENABLE_PHASE2=true" >> .env
```

### 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ襍ｷ蜍墓凾縺ｮ繧ｨ繝ｩ繝ｼ

**蜴溷屏**: BatchService縺ｮ繧､繝ｳ繝昴・繝医お繝ｩ繝ｼ

**蟇ｾ蜃ｦ**:
```bash
# app/services/batch_service.py 縺悟ｭ伜惠縺吶ｋ縺薙→繧堤｢ｺ隱・
ls -la app/services/batch_service.py

# Python繝代せ繧堤｢ｺ隱・
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 莉雁ｾ後・諡｡蠑ｵ莠亥ｮ・

Phase 2螳溯｣・ｾ後∽ｻ･荳九・讖溯・霑ｽ蜉縺御ｺ亥ｮ壹＆繧後※縺・∪縺・

### Phase 2.1: 鬮伜ｺｦ縺ｪ繝舌ャ繝∫ｮ｡逅・
- 繝舌ャ繝∽ｸ譎ょ●豁｢/蜀埼幕讖溯・
- 繝舌ャ繝√く繝｣繝ｳ繧ｻ繝ｫ讖溯・縺ｮ蠑ｷ蛹・
- 繝舌ャ繝∝ｮ溯｡悟ｱ･豁ｴ縺ｮ讀懃ｴ｢繝ｻ繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ

### Phase 2.2: 逶｣隕悶・騾夂衍讖溯・
- 繝舌ャ繝∝ｮ溯｡後Γ繝医Μ繧ｯ繧ｹ縺ｮ蜿朱寔繝ｻ蜿ｯ隕門喧
- 逡ｰ蟶ｸ讀懃衍縺ｨ繧｢繝ｩ繝ｼ繝域ｩ溯・
- 螳御ｺ・繧ｨ繝ｩ繝ｼ譎ゅ・Slack/繝｡繝ｼ繝ｫ騾夂衍

### Phase 3: 繧ｹ繧ｱ繝ｼ繝ｩ繝薙Μ繝・ぅ
- 蛻・淵蜃ｦ逅・ｯｾ蠢・
- 繧ｭ繝･繝ｼ・・Q/Celery・牙ｰ主・
- 繝ｭ繝ｼ繝峨ヰ繝ｩ繝ｳ繧ｷ繝ｳ繧ｰ

## 蜿り・ｳ・侭

- [蜈ｨ驫俶氛荳諡ｬ蜿門ｾ励す繧ｹ繝・Β莉墓ｧ俶嶌](./api_bulk_fetch.md)
- [繝・・繧ｿ繝吶・繧ｹ險ｭ險・(./database_design.md)
- [Issue #85: Phase 1縺九ｉPhase 2縺ｸ縺ｮ遘ｻ陦悟ｮ溯｣・(https://github.com/TIMMY-WEST/STOCK-INVESTMENT-ANALYZER/issues/85)

## 縺ｾ縺ｨ繧・

Phase 1縺九ｉPhase 2縺ｸ縺ｮ遘ｻ陦後↓繧医ｊ縲∽ｻ･荳九・繝｡繝ｪ繝・ヨ縺悟ｾ励ｉ繧後∪縺・

笨・**豌ｸ邯壼喧**: 繧｢繝励Μ繧ｱ繝ｼ繧ｷ繝ｧ繝ｳ蜀崎ｵｷ蜍募ｾ後ｂ繝舌ャ繝∵ュ蝣ｱ縺御ｿ晄戟縺輔ｌ繧・
笨・**荳倶ｽ堺ｺ呈鋤諤ｧ**: 譌｢蟄倥・繧ｯ繝ｩ繧､繧｢繝ｳ繝医さ繝ｼ繝峨・螟画峩荳崎ｦ・
笨・**諡｡蠑ｵ諤ｧ**: 莉雁ｾ後・讖溯・霑ｽ蜉縺後＠繧・☆縺・ｨｭ險・
笨・**逶｣隕匁ｧ**: 繝・・繧ｿ繝吶・繧ｹ繧ｯ繧ｨ繝ｪ縺ｧ繝舌ャ繝∝ｮ溯｡悟ｱ･豁ｴ繧貞・譫仙庄閭ｽ

遘ｻ陦後・谿ｵ髫守噪縺ｫ陦後ｏ繧後￣hase 1縺ｨPhase 2縺悟・蟄倥☆繧句ｽ｢縺ｧ螳溯｣・＆繧後※縺・ｋ縺溘ａ縲√Μ繧ｹ繧ｯ繧呈怙蟆城剞縺ｫ謚代∴縺ｪ縺後ｉ譁ｰ讖溯・繧貞ｰ主・縺ｧ縺阪∪縺吶・
