# AWS AI/ML Services Assessment - Easy

## Overview
Get started with AWS AI/ML services by exploring pre-trained models and APIs. Learn to use Amazon Rekognition for image analysis, Amazon Comprehend for natural language processing, and Amazon Translate for language translation without needing machine learning expertise.

**Difficulty**: Easy  
**Prerequisites**: Basic AWS knowledge, S3 basics  
**Estimated Time**: 2-3 hours  

## Learning Objectives
- Use Amazon Rekognition for image and video analysis
- Analyze text with Amazon Comprehend
- Translate text with Amazon Translate
- Work with Amazon Polly for text-to-speech
- Integrate AI services with S3
- Handle IAM permissions for AI services

## Prerequisites
- AWS CLI configured
- Python 3.8+ with boto3
- Basic understanding of S3

---

## Tasks

### Task 1: S3 Bucket for AI/ML Assets
**Objective**: Create an S3 bucket to store images, videos, and text files for AI processing.

Create an S3 bucket for AI/ML content:
```bash
aws s3 mb s3://aiml-assets-{student_id}

# Create folder structure
aws s3api put-object --bucket aiml-assets-{student_id} --key images/
aws s3api put-object --bucket aiml-assets-{student_id} --key videos/
aws s3api put-object --bucket aiml-assets-{student_id} --key documents/
aws s3api put-object --bucket aiml-assets-{student_id} --key audio/
```

**Enable versioning**:
```bash
aws s3api put-bucket-versioning \
  --bucket aiml-assets-{student_id} \
  --versioning-configuration Status=Enabled
```

---

### Task 2: Amazon Rekognition - Label Detection
**Objective**: Use Rekognition to detect labels (objects, scenes) in images.

**Upload sample image**:
```bash
# Download a sample image (or use your own)
curl -o sample-image.jpg https://picsum.photos/800/600

# Upload to S3
aws s3 cp sample-image.jpg s3://aiml-assets-{student_id}/images/sample-image.jpg
```

**Detect labels using AWS CLI**:
```bash
aws rekognition detect-labels \
  --image '{"S3Object":{"Bucket":"aiml-assets-{student_id}","Name":"images/sample-image.jpg"}}' \
  --max-labels 10 \
  --min-confidence 75 \
  --region us-east-1 > labels-output.json
```

**Python script** (`scripts/detect_labels.py`):
```python
import boto3
import json

def detect_labels(bucket, key, student_id):
    rekognition = boto3.client('rekognition')
    
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=10,
        MinConfidence=75
    )
    
    print(f"Labels detected in {key}:")
    for label in response['Labels']:
        print(f"  - {label['Name']}: {label['Confidence']:.2f}%")
    
    # Save results
    with open(f'rekognition-labels-{student_id}.json', 'w') as f:
        json.dump(response, f, indent=2)

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    bucket = f"aiml-assets-{student_id}"
    key = "images/sample-image.jpg"
    detect_labels(bucket, key, student_id)
```

**Run**:
```bash
python scripts/detect_labels.py {student_id}
```

---

### Task 3: Amazon Rekognition - Face Detection
**Objective**: Detect faces and facial attributes in images.

**Upload image with faces**:
```bash
# Use an image with people (download or use your own)
aws s3 cp face-image.jpg s3://aiml-assets-{student_id}/images/face-image.jpg
```

**Detect faces**:
```bash
aws rekognition detect-faces \
  --image '{"S3Object":{"Bucket":"aiml-assets-{student_id}","Name":"images/face-image.jpg"}}' \
  --attributes "ALL" \
  --region us-east-1 > faces-output.json
```

**Python script** (`scripts/detect_faces.py`):
```python
import boto3
import json

def detect_faces(bucket, key, student_id):
    rekognition = boto3.client('rekognition')
    
    response = rekognition.detect_faces(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        Attributes=['ALL']
    )
    
    print(f"Faces detected: {len(response['FaceDetails'])}")
    
    for i, face in enumerate(response['FaceDetails'], 1):
        print(f"\nFace {i}:")
        print(f"  Age range: {face['AgeRange']['Low']}-{face['AgeRange']['High']}")
        print(f"  Gender: {face['Gender']['Value']} ({face['Gender']['Confidence']:.1f}%)")
        print(f"  Smile: {face['Smile']['Value']} ({face['Smile']['Confidence']:.1f}%)")
        print(f"  Emotions: {face.get('Emotions', [])[0]['Type'] if face.get('Emotions') else 'N/A'}")
    
    # Save results
    with open(f'rekognition-faces-{student_id}.json', 'w') as f:
        json.dump(response, f, indent=2)

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    bucket = f"aiml-assets-{student_id}"
    key = "images/face-image.jpg"
    detect_faces(bucket, key, student_id)
```

---

### Task 4: Amazon Rekognition - Text Detection (OCR)
**Objective**: Extract text from images using optical character recognition.

**Upload image with text**:
```bash
# Image containing text (signs, documents, etc.)
aws s3 cp text-image.jpg s3://aiml-assets-{student_id}/images/text-image.jpg
```

**Detect text**:
```bash
aws rekognition detect-text \
  --image '{"S3Object":{"Bucket":"aiml-assets-{student_id}","Name":"images/text-image.jpg"}}' \
  --region us-east-1 > text-output.json
```

**Python script** (`scripts/detect_text.py`):
```python
import boto3
import json

def detect_text(bucket, key, student_id):
    rekognition = boto3.client('rekognition')
    
    response = rekognition.detect_text(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    
    print(f"Text detected in {key}:")
    
    # Print detected lines
    for text in response['TextDetections']:
        if text['Type'] == 'LINE':
            print(f"  Line: {text['DetectedText']} (Confidence: {text['Confidence']:.1f}%)")
    
    # Save all detections
    with open(f'rekognition-text-{student_id}.json', 'w') as f:
        json.dump(response, f, indent=2)

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    bucket = f"aiml-assets-{student_id}"
    key = "images/text-image.jpg"
    detect_text(bucket, key, student_id)
```

---

### Task 5: Amazon Comprehend - Sentiment Analysis
**Objective**: Analyze sentiment (positive, negative, neutral, mixed) in text.

**Create sample text file**:
```bash
cat > sample-reviews.txt << 'EOF'
This product is absolutely amazing! I love it so much.
The service was terrible and I'm very disappointed.
It's okay, nothing special but does the job.
I have mixed feelings about this purchase.
EOF

# Upload to S3
aws s3 cp sample-reviews.txt s3://aiml-assets-{student_id}/documents/sample-reviews.txt
```

**Analyze sentiment**:
```bash
aws comprehend detect-sentiment \
  --text "This product is absolutely amazing! I love it so much." \
  --language-code en \
  --region us-east-1
```

**Python script** (`scripts/analyze_sentiment.py`):
```python
import boto3
import json

def analyze_sentiment(text, student_id):
    comprehend = boto3.client('comprehend')
    
    response = comprehend.detect_sentiment(
        Text=text,
        LanguageCode='en'
    )
    
    print(f"Text: {text[:100]}...")
    print(f"Sentiment: {response['Sentiment']}")
    print("Scores:")
    for sentiment, score in response['SentimentScore'].items():
        print(f"  {sentiment}: {score:.4f}")
    
    return response

def analyze_file(bucket, key, student_id):
    s3 = boto3.client('s3')
    comprehend = boto3.client('comprehend')
    
    # Download file
    obj = s3.get_object(Bucket=bucket, Key=key)
    content = obj['Body'].read().decode('utf-8')
    
    results = []
    for line in content.strip().split('\n'):
        if line.strip():
            result = analyze_sentiment(line, student_id)
            results.append({'text': line, 'sentiment': result})
            print("-" * 60)
    
    # Save results
    with open(f'comprehend-sentiment-{student_id}.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    bucket = f"aiml-assets-{student_id}"
    key = "documents/sample-reviews.txt"
    analyze_file(bucket, key, student_id)
```

---

### Task 6: Amazon Comprehend - Entity Detection
**Objective**: Extract entities (people, organizations, locations, dates) from text.

**Detect entities**:
```bash
aws comprehend detect-entities \
  --text "Amazon Web Services was founded by Andy Jassy in Seattle, Washington in 2006." \
  --language-code en \
  --region us-east-1
```

**Python script** (`scripts/detect_entities.py`):
```python
import boto3
import json

def detect_entities(text, student_id):
    comprehend = boto3.client('comprehend')
    
    response = comprehend.detect_entities(
        Text=text,
        LanguageCode='en'
    )
    
    print(f"Text: {text}")
    print(f"\nEntities detected: {len(response['Entities'])}")
    
    # Group by type
    entities_by_type = {}
    for entity in response['Entities']:
        entity_type = entity['Type']
        if entity_type not in entities_by_type:
            entities_by_type[entity_type] = []
        entities_by_type[entity_type].append(entity['Text'])
    
    for entity_type, texts in entities_by_type.items():
        print(f"\n{entity_type}:")
        for text in texts:
            print(f"  - {text}")
    
    # Save results
    with open(f'comprehend-entities-{student_id}.json', 'w') as f:
        json.dump(response, f, indent=2)

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    
    sample_texts = [
        "Amazon Web Services was founded by Andy Jassy in Seattle, Washington in 2006.",
        "Apple Inc. announced its new iPhone at an event in Cupertino on September 12, 2023.",
        "The meeting between President Biden and Prime Minister Johnson will take place in London next week."
    ]
    
    for text in sample_texts:
        detect_entities(text, student_id)
        print("\n" + "=" * 60 + "\n")
```

---

### Task 7: Amazon Translate - Language Translation
**Objective**: Translate text between languages.

**Translate text**:
```bash
aws translate translate-text \
  --text "Hello, how are you today?" \
  --source-language-code en \
  --target-language-code es \
  --region us-east-1
```

**Python script** (`scripts/translate_text.py`):
```python
import boto3
import json

def translate_text(text, source_lang, target_lang, student_id):
    translate = boto3.client('translate')
    
    response = translate.translate_text(
        Text=text,
        SourceLanguageCode=source_lang,
        TargetLanguageCode=target_lang
    )
    
    print(f"Source ({source_lang}): {text}")
    print(f"Target ({target_lang}): {response['TranslatedText']}")
    print()
    
    return response

def translate_multi_language(text, student_id):
    target_languages = ['es', 'fr', 'de', 'it', 'pt', 'ja', 'zh']
    
    results = []
    print(f"Original (en): {text}\n")
    
    for target_lang in target_languages:
        result = translate_text(text, 'en', target_lang, student_id)
        results.append({
            'source': 'en',
            'target': target_lang,
            'original': text,
            'translated': result['TranslatedText']
        })
    
    # Save results
    with open(f'translate-results-{student_id}.json', 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    
    sample_text = "Artificial Intelligence and Machine Learning are transforming the world."
    translate_multi_language(sample_text, student_id)
```

---

### Task 8: Amazon Polly - Text-to-Speech
**Objective**: Convert text to speech audio files.

**Synthesize speech**:
```bash
aws polly synthesize-speech \
  --text "Hello, welcome to AWS AI and ML services." \
  --output-format mp3 \
  --voice-id Joanna \
  --region us-east-1 \
  speech-output.mp3
```

**Python script** (`scripts/text_to_speech.py`):
```python
import boto3
import json

def text_to_speech(text, voice_id, student_id):
    polly = boto3.client('polly')
    
    response = polly.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice_id,
        Engine='neural'  # Use neural engine for better quality
    )
    
    # Save audio file
    filename = f'polly-{voice_id.lower()}-{student_id}.mp3'
    with open(filename, 'wb') as f:
        f.write(response['AudioStream'].read())
    
    print(f"Audio saved: {filename}")
    
    # Upload to S3
    s3 = boto3.client('s3')
    bucket = f"aiml-assets-{student_id}"
    s3.upload_file(filename, bucket, f"audio/{filename}")
    print(f"Uploaded to s3://{bucket}/audio/{filename}")

def list_voices():
    polly = boto3.client('polly')
    response = polly.describe_voices(Engine='neural')
    
    print("Available Neural Voices:")
    for voice in response['Voices'][:5]:  # Show first 5
        print(f"  - {voice['Id']} ({voice['LanguageCode']}) - {voice['Gender']}")

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    
    # List available voices
    list_voices()
    print()
    
    # Generate speech with different voices
    sample_text = "AWS provides powerful AI and machine learning services that are easy to use."
    
    voices = ['Joanna', 'Matthew', 'Amy']
    for voice in voices:
        text_to_speech(sample_text, voice, student_id)
```

---

### Task 9: IAM Role for AI Services
**Objective**: Create an IAM role with permissions for AI/ML services.

**Create IAM role**:
```bash
# Trust policy
cat > aiml-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "rekognition.amazonaws.com",
          "comprehend.amazonaws.com",
          "translate.amazonaws.com",
          "polly.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name AWSAIMLServicesRole-{student_id} \
  --assume-role-policy-document file://aiml-trust-policy.json

# Attach S3 read policy
aws iam attach-role-policy \
  --role-name AWSAIMLServicesRole-{student_id} \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create inline policy for AI services
cat > aiml-permissions-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:DetectLabels",
        "rekognition:DetectFaces",
        "rekognition:DetectText",
        "comprehend:DetectSentiment",
        "comprehend:DetectEntities",
        "translate:TranslateText",
        "polly:SynthesizeSpeech"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name AWSAIMLServicesRole-{student_id} \
  --policy-name AIMLServicesPolicy \
  --policy-document file://aiml-permissions-policy.json
```

---

### Task 10: Integrated AI Pipeline
**Objective**: Create a script that combines multiple AI services.

**Python script** (`scripts/ai_pipeline.py`):
```python
import boto3
import json
import sys

def ai_pipeline(student_id):
    """
    Complete AI pipeline:
    1. Detect labels in image
    2. Extract text from image
    3. Translate extracted text
    4. Analyze sentiment of translation
    5. Convert to speech
    """
    
    bucket = f"aiml-assets-{student_id}"
    image_key = "images/sample-image.jpg"
    
    # Initialize clients
    rekognition = boto3.client('rekognition')
    comprehend = boto3.client('comprehend')
    translate_client = boto3.client('translate')
    polly = boto3.client('polly')
    
    print("=" * 60)
    print("AI/ML Services Pipeline")
    print("=" * 60)
    
    # Step 1: Detect labels
    print("\n1. Detecting labels in image...")
    labels = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': image_key}},
        MaxLabels=5
    )
    print(f"   Found {len(labels['Labels'])} labels:")
    for label in labels['Labels'][:3]:
        print(f"   - {label['Name']} ({label['Confidence']:.1f}%)")
    
    # Step 2: Detect text
    print("\n2. Extracting text from image...")
    text_detection = rekognition.detect_text(
        Image={'S3Object': {'Bucket': bucket, 'Name': image_key}}
    )
    detected_text = " ".join([
        item['DetectedText'] 
        for item in text_detection['TextDetections'] 
        if item['Type'] == 'LINE'
    ])
    
    if detected_text:
        print(f"   Detected text: {detected_text[:100]}")
        
        # Step 3: Translate
        print("\n3. Translating text to Spanish...")
        translation = translate_client.translate_text(
            Text=detected_text,
            SourceLanguageCode='en',
            TargetLanguageCode='es'
        )
        translated_text = translation['TranslatedText']
        print(f"   Translation: {translated_text[:100]}")
        
        # Step 4: Sentiment analysis
        print("\n4. Analyzing sentiment...")
        sentiment = comprehend.detect_sentiment(
            Text=detected_text,
            LanguageCode='en'
        )
        print(f"   Sentiment: {sentiment['Sentiment']}")
        
        # Step 5: Text to speech
        print("\n5. Converting to speech...")
        speech = polly.synthesize_speech(
            Text=detected_text[:200],  # Limit length
            OutputFormat='mp3',
            VoiceId='Joanna'
        )
        
        output_file = f'pipeline-output-{student_id}.mp3'
        with open(output_file, 'wb') as f:
            f.write(speech['AudioStream'].read())
        print(f"   Audio saved: {output_file}")
    else:
        print("   No text detected in image")
    
    # Save pipeline results
    results = {
        'labels': labels['Labels'][:5],
        'text': detected_text,
        'translation': translated_text if detected_text else None,
        'sentiment': sentiment if detected_text else None
    }
    
    with open(f'ai-pipeline-results-{student_id}.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    student_id = sys.argv[1]
    ai_pipeline(student_id)
```

**Run pipeline**:
```bash
python scripts/ai_pipeline.py {student_id}
```

---

## Validation Commands

```bash
# Check S3 bucket exists
aws s3 ls s3://aiml-assets-{student_id}/

# Verify scripts directory
ls -la scripts/

# Check output files exist
ls -la *.json *.mp3

# Test each script
python scripts/detect_labels.py {student_id}
python scripts/detect_faces.py {student_id}
python scripts/analyze_sentiment.py {student_id}
python scripts/translate_text.py {student_id}

# Run full pipeline
python scripts/ai_pipeline.py {student_id}
```

---

## Success Criteria

✅ **S3 Bucket**: aiml-assets-{student_id} exists with folder structure  
✅ **Rekognition**: Labels, faces, and text detected from images  
✅ **Comprehend**: Sentiment and entities extracted from text  
✅ **Translate**: Text translated to multiple languages  
✅ **Polly**: Speech audio files generated  
✅ **IAM Role**: Role with AI/ML permissions created  
✅ **Scripts**: All Python scripts in `scripts/` directory  
✅ **Pipeline**: Integrated AI pipeline runs successfully  
✅ **Output Files**: JSON and MP3 files generated  

---

## Testing Your Work

Run the validation script:
```bash
python validate_tasks.py aiml_easy
```

The script will verify:
- S3 bucket exists with correct structure
- Sample images/documents uploaded
- Python scripts are present
- Output files generated (JSON, MP3)
- IAM role exists with correct permissions
- AI services are accessible

**Minimum passing score**: 70% (7 out of 10 tasks)

---

## Additional Resources

- [Amazon Rekognition Documentation](https://docs.aws.amazon.com/rekognition/)
- [Amazon Comprehend Documentation](https://docs.aws.amazon.com/comprehend/)
- [Amazon Translate Documentation](https://docs.aws.amazon.com/translate/)
- [Amazon Polly Documentation](https://docs.aws.amazon.com/polly/)
- [AWS AI Services Overview](https://aws.amazon.com/machine-learning/ai-services/)

---

## Cost Considerations

**Pricing (Pay per use)**:
- Rekognition: ~$1 per 1,000 images
- Comprehend: ~$0.0001 per unit (100 characters)
- Translate: ~$15 per million characters
- Polly: ~$4 per 1 million characters

**Estimated Cost**: $0.50-$1.00 for this assessment

---

## Next Steps

After completing this assessment:
1. ✅ Explore video analysis with Rekognition
2. ✅ Try custom comprehend models
3. ✅ Experiment with different Polly voices and languages
4. ✅ Move to AI/ML Medium assessment (SageMaker)

**Good luck with your AI/ML Easy assessment!** 🚀
