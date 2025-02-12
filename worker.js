export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    try {
      const body = await request.json();
      
      // Validate required fields
      if (!body.email || !body.file_content) {
        return new Response(
          JSON.stringify({ 
            ok: false, 
            error: 'Missing required fields: email and file_content' 
          }), 
          { 
            status: 400,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*'
            }
          }
        );
      }

      // Forward to GitHub API
      const githubResponse = await fetch(
        `https://api.github.com/repos/${env.GITHUB_OWNER}/${env.GITHUB_REPO}/dispatches`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'Cloudflare-Worker'
          },
          body: JSON.stringify({
            event_type: 'process-csv',
            client_payload: {
              email: body.email,
              file_content: body.file_content
            }
          })
        }
      );

      // Get response details if available
      let responseDetails = '';
      try {
        responseDetails = await githubResponse.text();
      } catch (e) {
        responseDetails = 'No response details available';
      }

      return new Response(
        JSON.stringify({ 
          ok: githubResponse.ok,
          status: githubResponse.status,
          statusText: githubResponse.statusText,
          details: responseDetails
        }), 
        { 
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        }
      );

    } catch (error) {
      return new Response(
        JSON.stringify({ 
          ok: false, 
          error: error.message 
        }), 
        { 
          status: 500,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        }
      );
    }
  }
}; 