# Testing AI Extraction v3.0 with Kia Seltos Images

## Option 1: Test via Frontend (Recommended)

The easiest way to test is through the web interface:

1. **Save the 4 Kia Seltos images** from the chat to your computer
   - damage_front_1.jpg (front view with debris)
   - damage_detail_2.jpg (close-up of damaged headlight)
   - damage_front_3.jpg (another front angle)
   - front_view_plate.jpg (showing license plate KL07CU7475)

2. **Open the frontend**: http://localhost:5173

3. **Login** with test credentials:
   - Email: `test@example.com`
   - Password: `test123`

4. **Submit a claim**:
   - Upload the 4 images
   - Description: "Front-end collision damage. Bumper crushed, hood bent, headlight damaged."
   - Submit

5. **Wait for AI analysis** (~10-15 seconds)

6. **View results**:
   ```bash
   python view_forensics.py
   ```

## Option 2: Test via Script

If you want to test the extraction directly:

1. **Save images** to: `server/test_images/kia_seltos/`
   - Name them: damage_front_1.jpg, damage_detail_2.jpg, damage_front_3.jpg, front_view_plate.jpg

2. **Run test script**:
   ```bash
   python test_kia_extraction.py
   ```

## Expected Results

With these damage images, the v3.0 system should extract:

### Identity
- **Vehicle**: Kia Seltos (2020, Red/Maroon)
- **License Plate**: KL07CU7475 ✓ (matches policy)
- **Plate Visible**: True
- **Detected Objects**: ["car", "damage_area", "debris"]

### Damage
- **Damage Detected**: True
- **Damage Type**: "crush" or "shatter"
- **Severity Score**: ~0.6-0.8 (moderate to severe)
- **Impact Point**: "front_center"
- **Damaged Panels**: ["front_bumper", "hood", "headlight_left", "fender_left"]
- **Paint Damage**: True
- **Glass Damage**: True (headlight)
- **Parts Missing**: Possibly true (bumper pieces)
- **Debris Visible**: True
- **Cost Range**: ₹80,000 - ₹150,000 (estimated)

### Forensics
- **Screen Recapture**: False
- **Image Quality**: "medium" or "high"
- **Lighting Quality**: "good" (outdoor daylight)
- **Is Blurry**: False

### Scene
- **Location Type**: "street" or "residential"
- **Time of Day**: "day"
- **Weather**: "clear"
- **Debris Visible**: True (glass/plastic pieces on ground)
- **Other Vehicles**: True (visible in background)

### Rule-Based Decisions
- **Fraud Score**: ~0.0-0.1 (very low - legitimate damage)
- **Fraud Probability**: "VERY_LOW"
- **Risk Flags**: [] (none expected - clean images)
- **Recommendation**: "REVIEW" (due to severity)
- **Review Priority**: "MEDIUM" or "HIGH"
- **Overall Confidence**: 85-100%

## Fraud Detection Test Cases

To test the fraud detection rules, try these scenarios:

1. **Screenshot Test**: Take a screenshot of one of the images and upload it
   - Expected: `is_screen_recapture: true`, `fraud_score: +0.4`

2. **Old Damage Test**: Upload images of a rusty, weathered vehicle
   - Expected: `is_rust_present: true`, `fraud_score: +0.3`

3. **Obscured Plate**: Cover/blur the license plate
   - Expected: `license_plate_obscured: true`, `fraud_score: +0.3`
