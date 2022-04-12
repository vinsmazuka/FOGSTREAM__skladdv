function openMenuCategories() {
	let menuCategories = document.getElementsByClassName('menu__categories')[0];
	menuCategories.style.display = 'flex';
}

function closeMenuCategories() {
	let menuCategories = document.getElementsByClassName('menu__categories')[0];
	menuCategories.style.display = 'none';
}

function openSubcategory(idSubcategory) {
	let subcategories = document.getElementsByClassName('subcategories')[0].childNodes;

	for(var i=0; i<subcategories.length; i++) {
		try {
			if (subcategories[i].classList.contains('subcategory')) {
				subcategories[i].style.display = 'none';
			}
		} catch {
			//pass
		}
		
	}

	let subcategory = document.getElementById(idSubcategory);
	subcategory.style.display = 'block';
}
