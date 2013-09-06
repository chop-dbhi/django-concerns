# django-concerns

A good use of thiapp was in a web app containing de-identifed patient information


## Install

```bash
pip install django-concerns
```


## Setup

Add `concerns` to `INSTALLED_APPS` along with the following Django contrib apps:

```python
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'concerns',
    ...
)
```

At a minimum, the following middleware must be installed:

```python
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)
```

Include the `concerns.urls` in the the `ROOT_URLCONF`:

```python
from django.conf.urls import url, patterns, include

urlpatterns = patterns('',
    url(r'^concerns/', include('concerns.urls')),
    ...
)
```


## Settings

- `CONCERN_EMAIL_SUBJECT` - The subject-line of the email sent to managers. Defaults to `Concern Report for {site}` where `{site}` is a string formatting variable for the current site's name, e.g. `Concern Report for example.com`
- `CONCERN_RESOLVERS` - A list or tuple with the same structure as `ADMINS` and `MANAGERS` of users who should receive an email when a concern is reported.
- `CONCERN_STATUSES` - A list of statuses that a reported concern could be in during review. The first status in the list is used as the default for new concerns. Default are `New`, `In Review`, `Duplicate`, and `Closed`.


## Templates

The templates that come with the django-concerns are functional, but _very_ minimal:

- `concerns/concern_list.html` - Renders a list of concerns with links to their detail pages
    - Context received:
        - `concerns` - `Concern` queryset
- `concerns/concern_detail.html`
    - Context received:
        - `concern` - `Concern` instance
        - `form` - Minimal form for resolving the concern.
- `concerns/report_concern.html`
    - Context recieved:
        - `form` - Minimal form for reporting a concern.

An email template is also provided and can be customized as well:

- `concerns/concern_email.txt`
    - Context recieved:
        - `protocol` - The site's protocol, either `http` or `https` for constructing the permalink to the concern detail page.
        - `site` - The `site` object which contains the domain for constructing the permalink.
        - `concern` - The `concern` instance itself for including details about the concern or getting the absolute URL.


## Usage

The recommended way for exposing a "report a concern" form in your application is having button that opens an in-page modal/dialog for filling out details of the concern. Most likely the concern they have is about something on the page they are currently viewing, so directing them to a separate page to fill out the form is not generally a good idea since they will lose the exact state of the page (in case it is not static).

The `Concern` model has a field `document` that is used for storing the HTML captured at the time of the concern was reported. JavaScript can be used to capture the HTML in the current state. We recommend using [jquery.freeze](http://cbmi.github.io/jquery.freeze/) which makes it trivial to _freeze_ the current state of the DOM. Note that if a modal is used, it should be hidden prior to freeze the DOM, otherwise the modal will visible in the HTML when the concern is reported.

```javascript
// Bind to button or listen for a event, freeze the dom and send
// a POST to log the document. The server-side could write the data
// to an HTML file for later viewing.
$('#freezer').click(function(event) {
    event.preventDefault();
    $.post('/screenlog/', $.param({document: $.freeze()}));
});
```

### Example: Bootstrap's Modal

This example assumes [Bootstrap 2.3.2](http://getbootstrap.com/2.3.2/) is being used (version 3 requires minor changes) as well as jquery.freeze.js (recommended above).

**Modal HTML markup**

```html
<div id="report-concern-modal" class="modal hide">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3>Report Concern</h3>
    </div>

    <div class="modal-body">
        <p>When you click "Submit Concern", a copy of this Web page will be sent to the administrators. Please provide any additional details regarding the concern we might not be able to see on the page.</p>
        <textarea class="input-block-level" rows="4" placeholder="Please describe the nature of the concern (optional)"></textarea>
    </div>

    <div class="modal-footer">
        <button class="btn" data-dismiss="modal">Cancel</button>
        <button data-submit="modal" data-url="/concerns/report/" class="btn btn-primary">Submit Concern</button>
    </div>
</div>
```

**Anchor/button to open the modal**

```html
<a id="report-concern-toggle" href="#report-concern-modal" role="button" class="btn" data-toggle="modal">Report Concern</a>
```


**JavaScript containing the submission logic**

```javascript
// Various elements of interest
var concernButton = $('#report-concern-toggle'),
    concernModal = $('#report-concern-modal'),
    concernComment = concernModal.find('textarea'),
    concernSubmit = concernModal.find('[data-submit]');

// In the unlikely event the POST fails, show a fallback message containing
// and email address the user can contact directly.
var fallbackMessage = '<p class="text-error">Unfortunately the submission \
    failed. Please contact us at <a href="mailto:foo@example.com">foo@example.com</a> \
    with as much detail as you can about the nature of the concern. Thank you.</p>'

// Bind to click event of the submission button
concernSubmit.on('click', function(event) {
    event.preventDefault();
    // Hide the modal before freezing the DOM
    concernModal.modal('hide');

    var data = $.param({
        document: $.freeze(),
        comment: concernComment.val(),
    });

    $.ajax({
        type: 'POST',
        data: data,
        url: concernSubmit.data('url'),
        success: function(resp) {
            // Clear comment box, temporarily show 'thank you' message on button
            concernComment.val('');

            var buttonText = concernButton.text();
            concernButton.addClass('btn-success').text('Submitted. Thank You!')
            setTimeout(function() {
                concernButton.removeClass('btn-success').text(buttonText);
            }, 3000);
        },
        error: function(xhr, code, error) {
            // Re-open modal with fallback message
            concernModal.modal('open');
            concernComment.before(fallbackMessage);
        }
    });
});
```
