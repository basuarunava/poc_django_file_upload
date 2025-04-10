import datetime
from django.shortcuts import render, redirect
from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, storage, firestore


if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'pocdjangofileupload.firebasestorage.app'
    })

db = firestore.client()
bucket = storage.bucket()

def upload_file(request):
    if request.method == "POST" and "file" in request.FILES:
        file = request.FILES["file"]
        blob = bucket.blob(file.name)
        blob.upload_from_file(file)

        file_data = {
            "filename": file.name,
            "size": file.size,
            "uploaded_on": datetime.datetime.utcnow(),
            "last_opened_on": None
        }
        db.collection("files").document(file.name).set(file_data)
        return redirect("home")

    # GET request: show files
    files = db.collection("files").stream()
    files_data = [f.to_dict() for f in files]
    return render(request, "home.html", {"files": files_data})

def open_file(request, filename):
    db.collection("files").document(filename).update({
        "last_opened_on": datetime.datetime.utcnow()
    })
    return JsonResponse({"status": "ok"})
