import { Container, getContainer } from "@cloudflare/containers";

interface Env {
  SLATERUNNER: DurableObjectNamespace<SlateRunnerContainer>;
  BOOT_TOKEN?: string;
  CF_ACCOUNT_ID?: string;
  D1_DATABASE_ID?: string;
  D1_API_TOKEN?: string;
}

export class SlateRunnerContainer extends Container<Env> {
  defaultPort = 8000;
  sleepAfter = "10m";

  constructor(ctx: DurableObjectState<{}>, env: Env) {
    super(ctx, env);
    this.envVars = {
      ENVIRONMENT: "production",
      BOOT_TOKEN: env.BOOT_TOKEN ?? "",
      CF_ACCOUNT_ID: env.CF_ACCOUNT_ID ?? "",
      D1_DATABASE_ID: env.D1_DATABASE_ID ?? "",
      D1_API_TOKEN: env.D1_API_TOKEN ?? "",
    };
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    return getContainer(env.SLATERUNNER).fetch(request);
  },
} satisfies ExportedHandler<Env>;
