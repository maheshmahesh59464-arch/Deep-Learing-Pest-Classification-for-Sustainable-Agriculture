import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
from PIL import Image
import os
from django.core.files.storage import default_storage
from django.conf import settings
import uuid

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_model_and_generate_plots():
    DATA_DIR = os.path.join(settings.BASE_DIR, "media", "pest_data")
    BATCH_SIZE = 32
    NUM_EPOCHS = 5
    NUM_CLASSES = 12
    LEARNING_RATE = 0.001

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
        # If directory is empty, we might want to handle it, but for now we assume it has data
        
    dataset = datasets.ImageFolder(DATA_DIR, transform=transform)

    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size

    train_data, val_data = torch.utils.data.random_split(dataset, [train_size, val_size])

    train_loader = DataLoader(train_data, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=BATCH_SIZE, shuffle=False)

    model = models.resnet18(pretrained=True)
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    train_losses = []
    accuracies = []

    for epoch in range(NUM_EPOCHS):

        model.train()
        running_loss = 0
        correct = 0
        total = 0

        for images, labels in train_loader:

            images, labels = images.to(device), labels.to(device)

            outputs = model(images)
            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

            _, predicted = torch.max(outputs.data, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

        accuracy = 100 * correct / total

        train_losses.append(running_loss)
        accuracies.append(accuracy)

    # Validation
    model.eval()

    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in val_loader:

            images, labels = images.to(device), labels.to(device)

            outputs = model(images)

            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

    val_accuracy = 100 * correct / total

    # Plot
    plt.plot(train_losses, label="Loss")
    plt.plot(accuracies, label="Accuracy")
    plt.xlabel("Epochs")
    plt.legend()

    plot_dir = os.path.join(settings.BASE_DIR, "static", "plots")
    os.makedirs(plot_dir, exist_ok=True)
    plot_path = os.path.join(plot_dir, "train_plot.png")

    plt.savefig(plot_path)
    plt.clf()

    model_path = os.path.join(settings.BASE_DIR, "media", "pest_cnn_model.pth")
    torch.save(model.state_dict(), model_path)

    return {
        'plot_path': "plots/train_plot.png",
        'val_accuracy': val_accuracy,
        'train_accuracy': accuracies[-1],
        'loss': train_losses[-1],
    }


def predict_pest(image_file):

    class_names = [
        "Ants", "Bees", "Beetles", "Caterpillars", "Earthworms", "Earwigs",
        "Grasshoppers", "Moths", "Slugs", "Snails", "Wasps", "Weevils"
    ]

    harmful_classes = {
        "Caterpillars", "Grasshoppers", "Moths",
        "Slugs", "Snails", "Weevils"
    }

    beneficial_classes = {
        "Bees", "Ants", "Earthworms", "Wasps", "Earwigs", "Beetles"
    }

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(class_names))

    model_path = os.path.join(settings.BASE_DIR, "media", "pest_cnn_model.pth")
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))

    model.to(device)
    model.eval()

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    image = Image.open(image_file).convert("RGB")
    image = transform(image).unsqueeze(0).to(device)

    eco_solutions = {
        "Caterpillars": "Use Neem oil spray or Bacillus thuringiensis (Bt) for effective control.",
        "Grasshoppers": "Apply garlic spray or introduce natural predators like birds to your garden.",
        "Moths": "Use pheromone traps or light traps to disrupt their lifecycle naturally.",
        "Slugs": "Create barriers with crushed eggshells or use copper tape around plants.",
        "Snails": "Set up beer traps or relocate them manually away from your sustainable crops.",
        "Weevils": "Use Diatomaceous earth or neem-based organic insecticides around the soil."
    }

    with torch.no_grad():
        outputs = model(image)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        max_prob, predicted = torch.max(probabilities, 1)

    predicted_class = class_names[predicted.item()]
    harmful_percentage = 0.0
    eco_solution = ""

    # If the confidence is too low, we flag it as an invalid image
    if max_prob.item() < 0.60:
        predicted_class = "Invalid Image"
        category = "Unknown"
    else:
        category = "Harmful" if predicted_class in harmful_classes else "Beneficial"
        if category == "Harmful":
            # Scale confidence to a realistic harmfulness percentage (70-98%)
            harmful_percentage = round(70 + (max_prob.item() * 28), 2)
            eco_solution = eco_solutions.get(predicted_class, "Maintain soil health and use organic compost.")
        else:
            harmful_percentage = 0.0
            eco_solution = "This pest is beneficial! It helps maintain ecosystem balance in sustainable farming."

    return predicted_class, category, harmful_percentage, eco_solution


def get_training_accuracy():

    DATA_DIR = os.path.join(settings.BASE_DIR, "media", "pest_data")
    BATCH_SIZE = 32
    NUM_CLASSES = 12

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])

    if not os.path.exists(DATA_DIR):
        return 0.0
        
    dataset = datasets.ImageFolder(DATA_DIR, transform=transform)

    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)

    model_path = os.path.join(settings.BASE_DIR, "media", "pest_cnn_model.pth")
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))

    model.to(device)
    model.eval()

    correct = 0
    total = 0

    with torch.no_grad():

        for images, labels in loader:

            images, labels = images.to(device), labels.to(device)

            outputs = model(images)

            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)

            correct += (predicted == labels).sum().item()

    if total == 0:
        return 0.0
        
    accuracy = 100 * correct / total

    return round(accuracy, 2)