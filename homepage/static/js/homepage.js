document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search");

  if (!searchInput) {
    return;
  }

  const iconCards = Array.from(
    document.querySelectorAll('[id^="link-"][data-title]'),
  ).map((element) => {
    return {
      element,
      title: element.dataset.title.toLowerCase(),
    };
  });

  searchInput.addEventListener("input", () => {
    const queryTerms = searchInput.value
      .trim()
      .toLowerCase()
      .split(/\s+/)
      .filter(Boolean);

    for (const iconCard of iconCards) {
      iconCard.element.hidden =
        queryTerms.length > 0 &&
        !queryTerms.every((queryTerm) => iconCard.title.includes(queryTerm));
    }
  });
});
