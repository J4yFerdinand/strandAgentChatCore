import { StackContext, Function, Api } from "sst/constructs";

export function API({ stack }: StackContext) {
  const apiFn = new Function(stack, "FastApiLambda", {
    runtime: "python3.12",
    handler: "packages/fastapi-app/main.handler",
  });

  const api = new Api(stack, "FastApi", {
    routes: {
      "GET /": apiFn,
      "GET /hello": apiFn,
      "POST /data": apiFn
    }
  });

  stack.addOutputs({
    ApiEndpoint: api.url
  });
}