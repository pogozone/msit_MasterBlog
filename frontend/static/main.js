// Function that runs once the window is fully loaded
window.onload = function() {
    // Attempt to retrieve the API base URL from the local storage
    var savedBaseUrl = localStorage.getItem('apiBaseUrl');
    // If a base URL is found in local storage, load the posts
    if (savedBaseUrl) {
        document.getElementById('api-base-url').value = savedBaseUrl;
        loadPosts();
    }
}

// Function to fetch all the posts from the API and display them on the page
function loadPosts() {
    // Retrieve the base URL from the input field and save it to local storage
    var baseUrl = document.getElementById('api-base-url').value;
    localStorage.setItem('apiBaseUrl', baseUrl);

    // Use the Fetch API to send a GET request to the /posts endpoint
    fetch(baseUrl + '/posts')
        .then(response => response.json())  // Parse the JSON data from the response
        .then(data => {  // Once the data is ready, we can use it
            // Clear out the post container first
            const postContainer = document.getElementById('post-container');
            postContainer.innerHTML = '';

            // For each post in the response, create a new post element and add it to the page
            data.forEach(post => {
                const postDiv = document.createElement('div');
                postDiv.className = 'post';
                postDiv.id = `post-${post.id}`;
                postDiv.innerHTML = HTML_post(post);
                postContainer.appendChild(postDiv);
            });
        })
        .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// show form to edit post
function editPost(postId) {
    const baseUrl = document.getElementById("api-base-url").value;

    fetch(baseUrl + "/posts?post_id=" + postId)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP-Fehler ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const postContainer = document.getElementById("post-container");
            postContainer.innerHTML = "";

            data.forEach(post => {
                const postDiv = document.createElement("div");
                postDiv.className = "post";
                postDiv.id = `post-${post.id}`;

                postDiv.innerHTML = `
                    <h2>Beitrag bearbeiten</h2>
                    <p>
                        <input type="text" name="edit-title" id="edit-title">
                    </p>
                    <p>
                        <textarea name="edit-content" id="edit-content"></textarea>
                    </p>
                    <p>
                        <input type="text" name="edit-author" id="edit-author">
                    </p>
                    <p class="edit-date"></p>
                    <button type="button" class="updateButton">Update</button>
                `;

                postDiv.querySelector("#edit-title").value = post.title ?? "";
                postDiv.querySelector("#edit-content").value = post.content ?? "";
                postDiv.querySelector("#edit-author").value = post.author ?? "";
                postDiv.querySelector(".edit-date").textContent = post.date ?? "";

                postDiv.querySelector(".updateButton")
                    .addEventListener("click", () => updatePost(post.id));

                postContainer.appendChild(postDiv);

            });
        })
        .catch(error => {
            console.error("Laden des Beitrags fehlgeschlagen:", error);
        });
}
// update post (PUT) and return to index
function updatePost(postId) {
    const baseUrl = document.getElementById("api-base-url").value;

    const postData = {
        title: document.getElementById("edit-title").value,
        content: document.getElementById("edit-content").value,
        author: document.getElementById("edit-author").value
    };

    fetch(baseUrl + "/posts/" + postId, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(postData)
    })
        .then(async response => {
            if (!response.ok) {
                const message = await response.text();
                throw new Error(
                    message || `HTTP-Fehler ${response.status}`
                );
            }

            loadPosts();
        })
        .catch(error => {
            console.error("Update fehlgeschlagen:", error);
        });
}

// Function to send a POST request to the API to add a new post
function addPost() {
    // Retrieve the values from the input fields
    var baseUrl = document.getElementById('api-base-url').value;
    var postTitle = document.getElementById('post-title').value;
    var postContent = document.getElementById('post-content').value;
    var postAuthor = document.getElementById('post-author').value;

    // Use the Fetch API to send a POST request to the /posts endpoint
    fetch(baseUrl + '/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: postTitle, content: postContent, author: postAuthor })
    })
    .then(response => {
         if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(JSON.stringify(errData));
            });
         }
         return response.json();
    })  // Parse the JSON data from the response
    .then(post => {
        console.log('Post added:', post);
        loadPosts(); // Reload the posts after adding a new one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

// Function to send a DELETE request to the API to delete a post
function deletePost(postId) {
    var baseUrl = document.getElementById('api-base-url').value;

    // Use the Fetch API to send a DELETE request to the specific post's endpoint
    fetch(baseUrl + '/posts/' + postId, {
        method: 'DELETE'
    })
    .then(response => {
        console.log('Post deleted:', postId);
        loadPosts(); // Reload the posts after deleting one
    })
    .catch(error => console.error('Error:', error));  // If an error occurs, log it to the console
}

/* search */
const searchField = document.getElementById("post-search");
let controller;

searchField.addEventListener("input", async () => {

    controller?.abort();
    controller = new AbortController();

    const baseUrl = document.getElementById("api-base-url").value;
    const query = encodeURIComponent(searchField.value);

    try {
        const response = await fetch(
            `${baseUrl}/posts/search?query_param=${query}`,
            { signal: controller.signal }
        );

        if (!response.ok) {
            throw new Error(`HTTP-Fehler ${response.status}`);
        }

        const posts = await response.json();
        if (posts.length === 0) {
            loadPosts();
            return;
        }

        const postContainer = document.getElementById('post-container');
        postContainer.innerHTML = '';

        // For each post in the response, create a new post element and add it to the page
        posts.forEach(post => {
            const postDiv = document.createElement('div');
            postDiv.className = 'post';
            postDiv.id = `post-${post.id}`;
            postDiv.innerHTML = HTML_post(post);
            postContainer.appendChild(postDiv);
        });

    } catch (error) {
        if (error.name !== "AbortError") {
            console.error("Suche fehlgeschlagen:", error);
        }
    }
});

/* HTML snippets */
const HTML_post = (post) => {
    return `
        <h2>${post.title}</h2><p>${post.content}</p>
        <p>${post.author}</p>
        <p>${post.date}</p>
        <div><button class="editButton" onclick="editPost(${post.id})">Edit</button></div>
        <div><button class="deleteButton" onclick="deletePost(${post.id})">Delete</button></div>
    `;
};