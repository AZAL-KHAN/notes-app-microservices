function openModal() {
  const modal = document.getElementById("modal");
  modal.style.display = "flex";

  // Auto-focus the textarea when modal opens
  setTimeout(() => {
    const textarea = document.getElementById("note-textarea");
    if (textarea) {
      textarea.focus();
    }
  }, 50);
}

function closeModal() {
  document.getElementById("modal").style.display = "none";
}
