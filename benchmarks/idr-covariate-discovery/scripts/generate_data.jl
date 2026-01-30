#=
IDR Covariate Discovery Benchmark - Data Generation Script

This script generates the synthetic Indirect Response (IDR) dataset for the 
covariate discovery benchmark. The data generation is fully reproducible via
StableRNGs with fixed seeds.

To run:
    julia --project=. generate_data.jl

Output:
    ../data/train.csv  (300 subjects)
    ../data/test.csv   (1000 subjects)

Reference:
    Adapted from PaperMaterial_DeepNLME/experiment/idr.jl
    Original paper: [DeepNLME paper citation]

Software:
    Developed for Pumas v2.8.0 but should be compatible with later v2.x versions.
=#

using Pkg
Pkg.activate(@__DIR__())
using Pumas
using StableRNGs
using DataFrames
using DataFramesMeta
using CSV
using Random: shuffle
using AlgebraOfGraphics
using CairoMakie
using SummaryTables

root_dir = abspath(joinpath(@__DIR__(), ".."))
data_dir = joinpath(root_dir, "data/")
asset_dir = joinpath(root_dir, "assets/")

mkpath(data_dir)
mkpath(asset_dir)


# =============================================================================
# Covariate Distributions
# =============================================================================
# Six abstract covariates with various distributions.
# These have nonlinear and interacting effects on model parameters.

const COV_DISTS = (;
  c1=Gamma(5, 2),   # Affects S_max (saturation relationship)
  c2=Gamma(7, 3),   # Affects n (power relationship)
  c3=Normal(),      # Affects K_a (interaction with c4)
  c4=Normal(),      # Affects K_a (interaction with c3)
  c5=Gamma(11, 1),  # Affects K_out (ratio with c6)
  c6=Gamma(11, 1),  # Affects K_out (ratio with c5)
)

# =============================================================================
# True Model Definition
# =============================================================================
# Indirect Response Model with Emax-type drug effect
#
# ODE System:
#   Depot'   = -K_a × Depot
#   Central' = K_a × Depot - (CL/V_c) × Central
#   R'       = K_in × (1 + EFF) - K_out × R
#
# Drug Effect:
#   EFF = S_max × cp^n / (SC_50^n + cp^n)
#
# Covariate Effects (nonlinear, by design):
#   K_a   ~ logistic(2 × c3 × c4)          [interaction]
#   K_out ~ c5 / (c5 + c6)                  [ratio/competition]
#   S_max ~ c1 / (10 + c1)                  [saturation]
#   n     ~ (c2 / 20)^0.75                  [power]

truemod = @model begin
  @param begin
    tvK_a ∈ RealDomain(; lower=0, init=1.904)
    tvCL ∈ RealDomain(; lower=0, init=1.5)
    tvV_c ∈ RealDomain(; lower=0, init=1.4)
    tvS_max ∈ RealDomain(; lower=0, init=0.9)
    tvn ∈ RealDomain(; lower=0, init=1.103)
    tvSC_50 ∈ RealDomain(; lower=0, init=0.1)
    tvK_out ∈ RealDomain(; lower=0, init=5.564)
    tvK_in ∈ RealDomain(; lower=0, init=2.2)
    Ω ∈ PDiagDomain(; init=[0.2, 0.1, 0.1, 0.2])
    σ_pk ∈ RealDomain(; lower=0, init=2e-2)
    σ_pd ∈ RealDomain(; lower=0, init=5e-2)
  end
  @random begin
    η ~ MvNormal(Ω)
  end
  @covariates c1 c2 c3 c4 c5 c6
  @pre begin
    # Covariate effects are nonlinear and interacting by design
    K_a = tvK_a * exp(η[1] + 1.5 * (logistic(2 * c3 * c4) - 0.5))
    V_c = tvV_c
    K_out = tvK_out * exp(η[2] + 1.6 * (c5 / (c6 + c5) - 0.5))
    S_max = tvS_max * exp(η[3] * 8 * (c1 / (10.0 + c1) - 0.476))
    n = tvn * exp(η[4] + 0.1 * ((c2 / 20)^0.75 - 1))
    K_in = tvK_in
    CL = tvCL
    SC_50 = tvSC_50
  end
  @init begin
    R = K_in / K_out
  end
  @vars begin
    cp = abs(max(Central / V_c, 1e-6))
    EFF = S_max * cp^n / (SC_50^n + cp^n)
  end
  @dynamics begin
    Depot' = -K_a * Depot
    Central' = K_a * Depot - (CL / V_c) * Central
    R' = K_in * (1 + EFF) - K_out * R
  end
  @derived begin
    y_pk ~ @. Normal(Central / V_c, σ_pk)
    y_pd ~ @. Normal(R, σ_pd)
  end
end

# =============================================================================
# Observation Time Generator
# =============================================================================
# Generates irregular observation times using a Gamma distribution
get_obstimes(rng; N=15, tstop=10) = cumsum(rand(rng, Gamma(7, tstop / (7N)), N))

# =============================================================================
# Population Generator
# =============================================================================
# Generates a population with:
# - Random number of doses (1-3) at random times
# - PK-focused early observations after each dose
# - Irregular sampling throughout
# - All 6 covariates sampled from their distributions

p_true = init_params(truemod)

n_train = 300
n_test = 1000
seed = 1234

df = mapreduce(vcat, 1:(n_train+n_test)) do i
  rng = StableRNG(i)

  # Random dosing: 1-3 doses at random times
  dosetimes = cumsum([0; rand(rng, Gamma(15, 2 / 14), rand(rng, 0:2))])

  # PK-focused early observations after each dose
  pk_obstimes = mapreduce(vcat, dosetimes) do t
    t .+ get_obstimes(rng; N=2, tstop=0.5)
  end

  # Combine regular and PK-focused observation times
  obstimes = sort(vcat(
    get_obstimes(rng; N=rand(rng, 6:10), tstop=10),
    dosetimes,
    pk_obstimes,
  ))

  # Create subject with covariates
  subj = Subject(;
    events=DosageRegimen((DosageRegimen(1, time=t) for t in dosetimes)...),
    covariates=NamedTuple{keys(COV_DISTS)}(rand.(rng, values(COV_DISTS))),
    id=i,
  )

  sim = simobs(truemod, subj, p_true; obstimes, rng=StableRNG(100 + i))

  df = @chain DataFrame(Subject(sim)) begin
    @select Not(:cp, :EFF, :ss, :ii, :route, :tad, :dosenum, :rate, :duration)
    @rtransform :cmt = ismissing(:cmt) ? missing : 1
    @transform :split = i ≤ n_train ? "train" : "test"
    @rtransform :y_pd = :time ∈ pk_obstimes ? missing : :y_pd
  end

  return df
end


begin
  df_sample = @subset df :id .∈ Ref(unique(:id)[1:12])

  dosespec = data(@rsubset df_sample :evid == 1)
  dosespec *= mapping(:time)
  dosespec *= visual(VLines, linestyle=:dash, linewidth=1, label="Dose event")

  _df = stack(df_sample, [:y_pk, :y_pd])
  spec = data(@rsubset(_df, !ismissing(:value)))
  spec *= mapping(:time, :value; color=:variable => "")
  spec *= visual(ScatterLines, markersize=6, linewidth=1)

  layoutspec = mapping(layout=:id => (x -> "Subject $x"))
  fig = draw(layoutspec * (dosespec + spec); legend=(; position=:top), figure=(; size=(800, 600)))
  save(asset_dir * "sample_trajectories.png", fig; px_per_unit=4)
end


tbl = overview_table(df)
open(asset_dir * "overview_table.html", "w") do f
  show(f, MIME("text/html"), tbl)
end


df_train = @rsubset(df, :split == "train")
df_test = @rsubset(df, :split == "test")
CSV.write(data_dir * "train.csv", df_train)
CSV.write(data_dir * "test.csv", df_test)


testpop = read_pumas(df_test; observations=[:y_pk, :y_pd], covariates=[:c1, :c2, :c3, :c4, :c5, :c6])
trainpop = read_pumas(df_train; observations=[:y_pk, :y_pd], covariates=[:c1, :c2, :c3, :c4, :c5, :c6])


approximations = [FOCE(), LaplaceI()]
_lls = mapreduce(vcat, approximations) do approx
  ll_test = loglikelihood(truemod, testpop, p_true, approx)
  ll_train = loglikelihood(truemod, trainpop, p_true, approx)
  DataFrame(; approximation=string(approx), Train=ll_train, Test=ll_test)
end
lls = stack(_lls, [:Train, :Test], variable_name="Data", value_name="Loglikelihood")

ll_table = listingtable(lls, :Loglikelihood => nothing, rows=[:Data], cols=[:approximation => "Approximated loglikelihood"])

open(asset_dir * "loglikelihoods.html", "w") do f
  show(f, MIME("text/html"), ll_table)
end

