# Deployment Guide for China Travel Kit

## 1. GitHub Repository Setup
1. Create a new GitHub repository named `china-travel-kit`.
2. In your local project root (`D:/独立站/china-travel-kit`), initialize git:
   ```bash
   git init
   git add .
   git commit -m "Initial China Travel Kit site"
   git branch -M main
   git remote add origin https://github.com/<your-username>/china-travel-kit.git
   git push -u origin main
   ```
3. If you already have an existing repository, simply add the remote and push.

## 2. Cloudflare Pages Deployment
1. Sign in to Cloudflare and open **Pages**.
2. Click **Create a project** and connect your GitHub account.
3. Select the `china-travel-kit` repository.
4. Use these build settings:
   - Framework preset: **None** or **Custom**
   - Build command: `npm run build`
   - Build output directory: `dist`
5. Set the environment variable if needed:
   - `NODE_VERSION` = `18`
6. Deploy the site.

## 3. Custom Domain Binding
1. In Cloudflare Pages, go to your project and open the **Custom domains** tab.
2. Add your domain and follow Cloudflare's DNS verification steps.
3. Create or update the DNS records to point the domain to Cloudflare Pages.
4. Enable HTTPS once the domain is verified.

## 4. Replacing Affiliate Placeholders
Search the codebase for placeholders and replace them with your actual affiliate URLs.
- `<!-- AFFILIATE_ESIM -->`
- `<!-- AFFILIATE_PAYMENT -->`
- `<!-- AFFILIATE_TRAVEL -->`

Example replacement in Markdown:
```md
<!-- AFFILIATE_ESIM -->
```
Replace with a real link block or button target in the content, for example:
```md
[Get the best China eSIM](https://example.com/affiliate?tag=yourtag)
```

## 5. Google AdSense Integration
1. Sign in to Google AdSense and create an account if you have not already.
2. Add your site and wait for approval.
3. Once approved, insert the AdSense script into `src/layouts/BaseLayout.astro` or `src/components/AdSlot.astro`.
4. Use `rel="sponsored nofollow"` on affiliate links and ad elements.

## 6. Post-Deployment Actions
1. Verify your site is live on the Cloudflare Pages URL and your custom domain.
2. Submit your sitemap URL to Google Search Console: `https://your-domain.com/sitemap.xml`.
3. Replace all placeholder site URLs with your actual domain in `astro.config.mjs` and `public/robots.txt`.
4. Replace placeholder email addresses in `src/pages/contact.astro` if needed.
5. Monitor page performance and content quality after launch.

## 7. Future Content Expansion
1. Add new guides to `src/content/posts/` with the same Frontmatter schema.
2. Keep each article in the same structure: introduction, preparation, step-by-step tutorial, FAQ, summary.
3. Rebuild and redeploy after each major content update:
   ```bash
   npm run build
   ```
