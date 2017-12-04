var test = require('tape');
var sanitize = require('./sanitize').sanitize;

test('Sanitize test', function (t) {
    t.plan(5)

    t.equal(
      sanitize('<a href="url">link text</a>'),
      '&#60;a href=&#34;url&#34;&#62;link text&#60;/a&#62;'
    )

    t.equal(
      sanitize('<img src="https://www.w3schools.com/html/pulpitrock.jpg" alt="Mountain View">'),
      '&#60;img src=&#34;https://www.w3schools.com/html/pulpitrock.jpg&#34; alt=&#34;Mountain View&#34;&#62;'
    )

    t.equal(
      sanitize('<div><a href="url">link text</a></div>'),
      '&#60;div&#62;&#60;a href=&#34;url&#34;&#62;link text&#60;/a&#62;&#60;/div&#62;'
    )

    t.equal(
      sanitize('<div><img src="https://www.w3schools.com/html/pulpitrock.jpg" alt="Mountain View"></div>'),
      '&#60;div&#62;&#60;img src=&#34;https://www.w3schools.com/html/pulpitrock.jpg&#34; alt=&#34;Mountain View&#34;&#62;&#60;/div&#62;'
    )

    t.equal(
      sanitize('<script>alert("💀")</script>'),
      '&#60;script&#62;alert(&#34;💀&#34;)&#60;/script&#62;'
    )

});
