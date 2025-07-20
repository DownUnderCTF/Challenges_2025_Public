FROM oven/bun:latest

COPY bun.lock package.json ./
COPY widget/package.json ./widget/
COPY backend/package.json ./backend/
RUN bun install --frozen-lockfile
COPY . ./

RUN cd widget && bun run build.ts

CMD ["bun", "run", "backend/src/app.ts"]
EXPOSE 3000